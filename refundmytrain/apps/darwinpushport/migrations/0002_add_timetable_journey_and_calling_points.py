# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-01 16:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('darwinpushport', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallingPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calling_point_type', models.CharField(max_length=2)),
                ('timetable_arrival_time', models.TimeField(null=True)),
                ('timetable_departure_time', models.TimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TimetableJourney',
            fields=[
                ('rtti_train_id', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('train_uid', models.CharField(db_index=True, max_length=6)),
                ('train_id', models.CharField(db_index=True, help_text='Train ID (Headcode)', max_length=4)),
                ('start_date', models.DateField(db_index=True)),
                ('operating_company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='darwinpushport.OperatingCompany')),
            ],
        ),
        migrations.AddField(
            model_name='callingpoint',
            name='journey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calling_points', to='darwinpushport.TimetableJourney'),
        ),
        migrations.AddField(
            model_name='callingpoint',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='darwinpushport.Location'),
        ),
    ]
