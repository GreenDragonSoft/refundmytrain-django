# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-21 17:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NaptanRailStation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tiploc', models.CharField(help_text='Timing Point Location - Codes relating to points used in deriving train schedules. Loaded from field `TiplocCode`', max_length=50, unique=True)),
                ('three_alpha', models.CharField(db_index=True, help_text='A 3-character code used for stations. Previously referred to as CRS (Computer Reservation System) or NRS (National Reservation System) codes. Loaded from field `CrsCode`', max_length=5)),
                ('name', models.CharField(db_index=True, help_text='Station name, with `Rail Station` removed from the end. Loaded from field `StationName`', max_length=256)),
            ],
        ),
    ]
