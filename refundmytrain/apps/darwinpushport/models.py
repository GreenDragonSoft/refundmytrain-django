import logging
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


class TimetableJourneyManager(models.Manager):
    def get_queryset(self):
        return super(TimetableJourneyManager, self) \
            .get_queryset().select_related('operating_company')


class TimetableJourney(models.Model):
    """
    Roughly matches the `Journey` field defined in the Darwin schedule file.
    """

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

    objects = TimetableJourneyManager()

    def __str__(self):
        return '{}'.format(self.rtti_train_id)

    def num_calling_points(self):
        return self.calling_points.all().count()

    def start(self):
        return self.calling_points.all().order_by('id').first()

    def end(self):
        return self.calling_points.all().order_by('id').last()

    def time_to_datetime(self, time):
        """
        For example if a train has a start date of 2nd April, a time of 01:00
        is going to be the next day (3rd April)
        """
        if isinstance(time, six.string_types):
            hour, minute = time.split(':')
            time = datetime.time(int(hour), int(minute))

        assert isinstance(time, datetime.time)

        if time.hour in [0, 1, 2, 3]:
            # if it's between midnight and 4am it's got to be the day *after*
            # the train was scheduled to begin
            day = self.start_date + datetime.timedelta(days=1)
        else:
            day = self.start_date

        combined = make_aware(datetime.datetime.combine(day, time))
        LOG.debug('{} + {} = {}'.format(self.start_date, time, combined))
        return combined


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

    journey = models.ForeignKey(
        TimetableJourney,
        related_name='calling_points',
    )

    location = models.ForeignKey(
        Location,
        related_name='+',
    )

    calling_point_type = models.CharField(
        max_length=2,
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

    def get_actual_arrival(self):
        return self.actual_arrival_time  # related field

    def actual_arrival_datetime(self):
        actual_arrival = self.actual_arrival_time
        return actual_arrival.datetime if actual_arrival else None

    def late_text(self):
        actual = self.actual_arrival_datetime()
        timetabled = self.timetable_arrival_datetime

        if actual is None or timetabled is None or actual <= timetabled:
            return None

        mins_late = int((actual - timetabled).total_seconds() / 60)

        if mins_late <= 0:
            return None

        return '{} mins late'.format(mins_late)

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
    timetabled_calling_point = models.OneToOneField(
        CallingPoint,
        related_name='actual_arrival_time',
    )

    time = models.TimeField()  # TODO: explain why this field is retaiend
    datetime = models.DateTimeField()


class ImportLog(models.Model):
    filename = models.CharField(max_length=100)
    import_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename


@receiver(pre_save)
def update_datetimes_from_times(sender, instance, **kwargs):
    if sender == CallingPoint:
        instance.timetable_arrival_datetime = (
            instance.journey.time_to_datetime(instance.timetable_arrival_time))
        instance.timetable_departure_datetime = (
            instance.journey.time_to_datetime(
                instance.timetable_departure_time))

    elif sender == ActualArrival:
        instance.datetime = (
            instance.timetabled_calling_point.journey.time_to_datetime(
                instance.time)
        )
