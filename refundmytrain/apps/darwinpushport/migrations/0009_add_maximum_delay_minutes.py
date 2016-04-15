# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-15 10:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('darwinpushport', '0008_add_journey_from_to_search_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetablejourney',
            name='maximum_minutes_late',
            field=models.PositiveSmallIntegerField(default=0, help_text='For trains with late arrivals at any calling point, this is the maximum recorded delay in minutes for any calling point'),
        ),
    ]
