# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-29 21:31
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import refundmytrain.libs.rail_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('operators', '0001_initial'),
        ('naptan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.UUIDField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='TrainEntity',
            fields=[
                ('train_id', refundmytrain.libs.rail_fields.TrainIDField(help_text='The 10-character unique identity for this train. This is used in other TRUST messages to identify the train.', max_length=10, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='TrainMovementMessage',
            fields=[
                ('message_id', models.UUIDField(help_text='Our own identifier: not part of TRUST or the rail system', primary_key=True, serialize=False)),
                ('train_id', refundmytrain.libs.rail_fields.TrainIDField(help_text='The 10-character unique identity for this train. This is used in other TRUST messages to identify the train.', max_length=10)),
                ('actual_datetime', models.DateTimeField(help_text='The date and time that this event happened at the location')),
                ('location_stanox', refundmytrain.libs.rail_fields.StanoxField(help_text='The STANOX of the location at which this event happened', max_length=6, validators=[django.core.validators.RegexValidator('\\d{5}\\*?')])),
                ('timetable_datetime', models.DateTimeField(help_text='The planned GBTT (passenger) date and time that the event was due to happen at this location', null=True)),
                ('planned_datetime', models.DateTimeField(help_text='The planned date and time that this event was due to happen at this location', null=True)),
                ('original_location_stanox', refundmytrain.libs.rail_fields.StanoxField(help_text='If the location has been revised, the STANOX of the location in the schedule at activation time', max_length=6, null=True, validators=[django.core.validators.RegexValidator('\\d{5}\\*?')])),
                ('original_location_datetime', models.DateTimeField(help_text='The planned departure time associated with the original location', null=True)),
                ('planned_event_type', refundmytrain.libs.rail_fields.TrainMovementEventField(choices=[('ARRIVAL', 'Arrival'), ('DEPARTURE', 'Departure'), ('DESTINATION', 'Destination')], help_text='The planned type of event - one of "ARRIVAL", "DEPARTURE" or "DESTINATION"', max_length=11)),
                ('event_type', refundmytrain.libs.rail_fields.TrainMovementEventField(choices=[('ARRIVAL', 'Arrival'), ('DEPARTURE', 'Departure'), ('DESTINATION', 'Destination')], help_text='The type of event - either "ARRIVAL" or "DEPARTURE"', max_length=11)),
                ('event_source', models.CharField(help_text='Whether the event source was "AUTOMATIC" from SMART, or "MANUAL" from TOPS or TRUST SDR', max_length=10)),
                ('is_correction', models.BooleanField(help_text='Whether this report is a correction of a previous report')),
                ('is_off_route', models.BooleanField(help_text='Whether this report is for a location OFF schedule')),
                ('direction', models.CharField(blank=True, help_text='For automatic reports, either "UP" or "DOWN" depending on the direction of travel', max_length=4, null=True)),
                ('line_indicator', models.CharField(blank=True, choices=[('F', 'Fast'), ('S', 'Slow')], help_text='A single character (or blank) depending on the line the train is travelling on, e.g. F = Fast, S = Slow', max_length=1, null=True)),
                ('platform', models.CharField(blank=True, help_text='Two characters (including a space for a single character) or blank if the movement report is associated with a platform number', max_length=3, null=True)),
                ('route', models.CharField(blank=True, help_text='A single character (or blank) to indicate the exit route from this location', max_length=1, null=True)),
                ('train_service_code', models.CharField(help_text='Train service code as per schedule', max_length=16)),
                ('timetable_variation', models.PositiveSmallIntegerField(help_text='The number of minutes variation from the scheduled time at this location. Off-route reports will contain "0"', null=True)),
                ('variation_status', models.CharField(choices=[('ON TIME', 'On time'), ('EARLY', 'Early'), ('LATE', 'Late'), ('OFF ROUTE', 'Off route')], help_text='One of "ON TIME", "EARLY", "LATE" or "OFF ROUTE"', max_length=10)),
                ('next_report_stanox', refundmytrain.libs.rail_fields.StanoxField(help_text='The STANOX of the location at which the next report for this train is due.', max_length=6, null=True, validators=[django.core.validators.RegexValidator('\\d{5}\\*?')])),
                ('next_report_run_time', models.PositiveSmallIntegerField(help_text='The running time to the next location in minutes.', null=True)),
                ('is_train_terminated', models.BooleanField(help_text='Whether the train has completed its journey.')),
                ('is_delay_monitoring_point', models.BooleanField(help_text='Whether this is a delay monitoring point. Off-route reports will contain "false"')),
                ('train_file_address', models.CharField(blank=True, help_text='The TOPS train file address, if applicable', max_length=16, null=True)),
                ('reporting_stanox', refundmytrain.libs.rail_fields.StanoxField(help_text='The STANOX of the location that generated this report. Set to "00000" for manual and off-route reports', max_length=6, null=True, validators=[django.core.validators.RegexValidator('\\d{5}\\*?')])),
                ('is_auto_expected', models.NullBooleanField(help_text='Whether an automatic report is expected for this location.')),
                ('current_train_entity', models.ForeignKey(help_text='Where a train has had its identity changed, the current 10-character unique identity for this train', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='changed_identity_train_movement_messages', to='trainmovements.TrainEntity')),
                ('location_station', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='naptan.NaptanRailStation')),
                ('next_report_station', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='next_report_train_movement_messages', to='naptan.NaptanRailStation')),
                ('operating_company', models.ForeignKey(help_text='Operating company ID as per TOC Codes', null=True, on_delete=django.db.models.deletion.CASCADE, to='operators.OperatingCompany')),
                ('original_location_station', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='changed_train_movement_messages', to='naptan.NaptanRailStation')),
                ('reporting_station', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reporting_station_train_movement_messages', to='naptan.NaptanRailStation')),
                ('train_entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='train_movement_messages', to='trainmovements.TrainEntity')),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='train_entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='trainmovements.TrainEntity'),
        ),
    ]
