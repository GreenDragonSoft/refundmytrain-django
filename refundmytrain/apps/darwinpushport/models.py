import logging
import itertools
import datetime

from collections import OrderedDict

import six

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import make_aware

LOG = logging.getLogger(__name__)


class OperatingCompany(models.Model):
    atoc_code = models.CharField(
        primary_key=True,
        max_length=2
    )

    name = models.CharField(
        db_index=True,
        max_length=256
    )

    def __str__(self):
        return '{} ({})'.format(self.name, self.atoc_code)


class Location(models.Model):
    tiploc = models.CharField(
        primary_key=True,
        max_length=10
    )

    three_alpha = models.CharField(
        null=True,
        unique=False,
        max_length=4
    )

    name = models.CharField(max_length=256)

    def __str__(self):
        return '{} ({})'.format(
            self.name,
            self.three_alpha if self.three_alpha else '-'
        )


class NonPassengerJourney(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    rtti_train_id = models.CharField(
        primary_key=True,
        max_length=15,
    )


class TimetableJourneyManager(models.Manager):
    def get_queryset(self):
        return super(TimetableJourneyManager, self) \
            .get_queryset().select_related('operating_company')


class TimetableJourney(models.Model):
    """
    Roughly matches the `Journey` field defined in the Darwin schedule file.
    """
    created_at = models.DateTimeField(auto_now_add=True)

    rtti_train_id = models.CharField(
        primary_key=True,
        max_length=15,
    )

    train_uid = models.CharField(
        db_index=True,
        max_length=6
    )

    train_id = models.CharField(
        db_index=True,
        max_length=4,
        help_text='Train ID (Headcode)',
    )

    start_date = models.DateField(
        db_index=True,
    )

    operating_company = models.ForeignKey(
        OperatingCompany
    )

    cancellation_reason = models.CharField(
        max_length=3,
        null=True,
        blank=True
    )

    maximum_minutes_late = models.PositiveSmallIntegerField(
        help_text=(
            'For trains with late arrivals at any calling point, this is the '
            'maximum recorded delay in minutes for any calling point'
        ),
        default=0
    )

    late_reason = models.CharField(
        max_length=3,
        null=True,
        blank=True
    )

    objects = TimetableJourneyManager()

    @property
    def public_calling_points(self):
        return [cp for cp in self.all_calling_points.all()
                if cp.public_visible]

    def __str__(self):
        return '{}'.format(self.rtti_train_id)

    def num_calling_points(self):
        return len(self.public_calling_points)

    def start(self):
        public_calling_points = self.public_calling_points
        return public_calling_points[0] if public_calling_points else None

    def end(self):
        public_calling_points = self.public_calling_points
        return public_calling_points[-1] if public_calling_points else None

    def time_to_datetime(self, time):
        """
        For example if a train has a start date of 2nd April, a time of 01:00
        is going to be the next day (3rd April)
        """
        if time is None:
            return None

        if isinstance(time, six.string_types):
            hour, minute = time.split(':')
            time = datetime.time(int(hour), int(minute))

        assert isinstance(time, datetime.time), type(time)

        if time.hour in [0, 1, 2, 3]:
            # if it's between midnight and 4am it's got to be the day *after*
            # the train was scheduled to begin
            day = self.start_date + datetime.timedelta(days=1)
        else:
            day = self.start_date

        combined = make_aware(datetime.datetime.combine(day, time))
        LOG.debug('{} + {} = {}'.format(self.start_date, time, combined))
        return combined

    def add_from_to_entries(self):
        for from_cp, to_cp in itertools.combinations(
                self.public_calling_points, 2):

            from_to, _ = JourneyFromTo.objects.get_or_create(
                from_location=from_cp.location,
                to_location=to_cp.location)

            from_to.journeys.add(self)


class CallingPointManager(models.Manager):
    def get_queryset(self):
        return super(CallingPointManager, self) \
            .get_queryset().select_related('location')


class CallingPoint(models.Model):
    TYPE_CHOICES = OrderedDict((
        ('OR', 'Passenger Origin'),
        ('OPOR', 'Operational Origin'),
        ('IP', 'Passenger Intermediate'),
        ('OPIP', 'Operational Intermediate'),
        ('PP', 'Intermediate Passing Point'),
        ('DT', 'Passenger Destination'),
        ('OPDT', 'Operational Destination'),
    ))

    class Meta:
        ordering = ['id']

    created_at = models.DateTimeField(auto_now_add=True)

    public_visible = models.BooleanField(default=True)

    journey = models.ForeignKey(
        TimetableJourney,
        related_name='all_calling_points',
    )

    location = models.ForeignKey(
        Location,
        related_name='+',
    )

    calling_point_type = models.CharField(
        max_length=4,
        choices=TYPE_CHOICES.items()
    )

    # TODO: explain why these `_time` fields are kept
    # A calling point may not have an arrival or a departure (if its an origin
    # or destination calling point) so these must be nullable.
    timetable_arrival_time = models.TimeField(null=True)
    timetable_departure_time = models.TimeField(null=True)
    timetable_arrival_datetime = models.DateTimeField(null=True)
    timetable_departure_datetime = models.DateTimeField(null=True)

    objects = CallingPointManager()

    def actual_arrival_time(self):
        """
        Return ActualArrival.time if this calling point has an associated
        actual arrival, else return None
        """
        if self.actual_arrival:
            return self.actual_arrival.time
        else:
            return None

    def late_text(self):
        if (self.timetable_arrival_time is None or
                self.actual_arrival is None):
            return None

        minutes_late = self.actual_arrival.minutes_late()

        if minutes_late:
            return '{} mins late'.format(minutes_late)
        else:
            return None

    def __str__(self):
        return self.location.name


class JourneyFromTo(models.Model):
    """
    from_to =  JourneyFromTo.objects.get(
            from_location__three_alpha='LIV',
            to_location__three_alpha='MCV',
        )
    journeys = from_to.journeys
    """

    class Meta:
        index_together = (
            ('from_location', 'to_location'),
        )
        unique_together = (
            ('from_location', 'to_location'),
        )

    from_location = models.ForeignKey(Location, related_name='+')
    to_location = models.ForeignKey(Location, related_name='+')
    journeys = models.ManyToManyField(TimetableJourney, related_name='+')

    def num_journeys(self):
        return self.journeys.count()


class ActualArrival(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    timetabled_calling_point = models.OneToOneField(
        CallingPoint,
        related_name='actual_arrival',
    )

    time = models.TimeField()  # TODO: explain why this field is retaiend
    datetime = models.DateTimeField()

    def to_datetime(self):
        return self.timetabled_calling_point.journey.time_to_datetime(
            self.time)

    def minutes_late(self):
        actual_dt = self.timetabled_calling_point.journey.time_to_datetime(
            self.time)
        timetable_dt = self.timetabled_calling_point.journey.time_to_datetime(
            self.timetabled_calling_point.timetable_arrival_time)

        if actual_dt is None or timetable_dt is None:
            raise ValueError('Missing actual or timetable datetime')

        return max(
            int((actual_dt - timetable_dt).total_seconds() / 60),
            0)


class ImportLog(models.Model):
    filename = models.CharField(max_length=100)
    import_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


class ReasonModel(models.Model):
    class Meta:
        abstract = True

    code = models.CharField(
        primary_key=True,
        max_length=3)

    text = models.CharField(max_length=256)


class CancellationReason(ReasonModel):
    pass


class LateRunningReason(ReasonModel):
    pass


@receiver(pre_save)
def update_datetimes_from_times(sender, instance, **kwargs):
    if sender == ActualArrival:
        instance.datetime = (
            instance.timetabled_calling_point.journey.time_to_datetime(
                instance.time)
        )
