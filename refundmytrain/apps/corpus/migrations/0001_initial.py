# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-20 23:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CorpusLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tiploc', models.CharField(blank=True, help_text='Timing Point Location - Codes relating to points used in deriving train schedules', max_length=50, null=True, unique=True)),
                ('three_alpha', models.CharField(blank=True, db_index=True, help_text='A 3-character code used for stations. Previously referred to as CRS (Computer Reservation System) or NRS (National Reservation System) codes.', max_length=5, null=True)),
                ('stanox', models.CharField(blank=True, db_index=True, help_text='Station Number - these codes can refer to non-station locations such as sidings and junctions. STANOX codes are grouped by geographical area - the first two digits specify the area in which the location exists.', max_length=10, null=True)),
                ('national_location_code', models.CharField(blank=True, help_text='(NLC) - A 6-digit code. These includes physical locations such as stations and junctions as well as codes relating to accounting and other purposes.', max_length=8, null=True, unique=True)),
                ('nlc_description', models.CharField(blank=True, help_text='Description of the national location code (NLC)', max_length=256, null=True)),
                ('nlc_short_description', models.CharField(blank=True, help_text='16-char description of the national location code (NLC)', max_length=16, null=True)),
            ],
        ),
    ]