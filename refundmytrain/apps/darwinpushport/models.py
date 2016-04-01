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
        return '{}: {} ({})'.format(
            self.tiploc,
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

    def num_calling_points(self):
        return self.calling_points.all().count()

    def start(self):
        return self.calling_points.all().order_by('id')[0]

    def end(self):
        return self.calling_points.all().order_by('id').reverse()[0]


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
        return None

    @property
    def timetable_departure_datetime(self):
        return None

    def __str__(self):
        return self.location.name
