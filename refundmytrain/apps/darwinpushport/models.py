import datetime

from collections import OrderedDict

from django.db import models


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

    def __str__(self):
        return '{}'.format(self.rtti_train_id)

    def num_calling_points(self):
        return self.calling_points.all().count()

    def start(self):
        return self.calling_points.all().order_by('id')[0]

    def end(self):
        return self.calling_points.all().order_by('id').reverse()[0]

    @property
    def earliest_possible_event(self):
        """
        Return the earliest possible datetime for an event happening on this
        journey. Effectively this is the time at which the day flips: we're
        saying 4am on the day of the journey is the earliest. This helps
        to categorise events after midnight to the correct day.
        """
        return datetime.datetime.combine(
            self.start_date,
            datetime.time(4)
        )


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

    timetable_arrival_time = models.TimeField(null=True)
    timetable_departure_time = models.TimeField(null=True)

    @property
    def timetable_arrival_datetime(self):
        return self.combine_date_time(self.timetable_arrival_time)

    @property
    def actual_arrival_datetime(self):
        return self.combine_date_time(self.actual_arrival_time.time)

    def combine_date_time(self, time):
        """
        For example if a train has a start date of 2nd April, a time of 01:00
        is going to be the next day (3rd April)
        """

        possible_datetime = datetime.datetime.combine(
            self.journey.start_date, time)

        if possible_datetime < self.journey.earliest_possible_event:
            return possible_datetime + datetime.timedelta(hours=24)

        else:
            return possible_datetime

    def late_text(self):
        actual = self.actual_arrival_datetime
        timetabled = self.timetable_arrival_datetime

        if actual is None:
            return None

        if actual <= timetabled:
            return None

        mins_late = int((actual - timetabled).total_seconds() / 60)

        if mins_late <= 0:
            return None

        return '{} mins late'.format(mins_late)

    def __str__(self):
        return self.location.name


class ActualArrival(models.Model):
    timetabled_calling_point = models.OneToOneField(
        CallingPoint,
        related_name='actual_arrival_time',
    )

    time = models.TimeField()


class ImportLog(models.Model):
    filename = models.CharField(max_length=100)
    import_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename
