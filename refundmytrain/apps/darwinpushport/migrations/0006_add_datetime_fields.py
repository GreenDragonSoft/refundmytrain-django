# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-05 16:50
from __future__ import unicode_literals

import datetime

from django.db import migrations, models
from django.db.models import Q
import django.db.models.deletion
from django.utils.timezone import make_aware


def time_to_datetime(time, journey):
    """
    For example if a train has a start date of 2nd April, a time of 01:00
    is going to be the next day (3rd April)
    """

    if time.hour in [0, 1, 2, 3]:
        # if it's between midnight and 4am it's got to be the day *after*
        # the train was scheduled to begin
        day = journey.start_date + datetime.timedelta(days=1)
    else:
        day = journey.start_date

    combined = make_aware(datetime.datetime.combine(day, time))
    return combined


def delete_calling_points_without_times(apps, schema_editor):
    CallingPoint = apps.get_model('darwinpushport', 'CallingPoint')

    CallingPoint.objects.filter(
        Q(timetable_departure_time__isnull=True) |
        Q(timetable_arrival_time__isnull=True)
    ).delete()


def populate_datetimes_from_times(apps, schema_editor):
    CallingPoint = apps.get_model('darwinpushport', 'CallingPoint')
    ActualArrival = apps.get_model('darwinpushport', 'ActualArrival')

    for calling_point in CallingPoint.objects.filter(
            Q(timetable_departure_datetime__isnull=True) |
            Q(timetable_arrival_datetime__isnull=True)):

        journey = calling_point.journey

        calling_point.timetable_departure_datetime = time_to_datetime(
            calling_point.timetable_departure_time, journey)

        calling_point.timetable_arrival_datetime = time_to_datetime(
            calling_point.timetable_arrival_time, journey)

        calling_point.save()

    for arrival in ActualArrival.objects.filter(datetime__isnull=True):
        journey = arrival.timetabled_calling_point.journey
        arrival.datetime = time_to_datetime(arrival.time, journey)
        arrival.save()


class Migration(migrations.Migration):

    dependencies = [
        ('darwinpushport', '0005_add_import_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='actualarrival',
            name='datetime',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='callingpoint',
            name='timetable_departure_datetime',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='callingpoint',
            name='timetable_arrival_datetime',
            field=models.DateTimeField(null=True),
        ),
        migrations.RunPython(delete_calling_points_without_times),
        migrations.RunPython(populate_datetimes_from_times),
    ]
