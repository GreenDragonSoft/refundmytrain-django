# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-01 14:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('tiploc', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('three_alpha', models.CharField(max_length=4, null=True)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='OperatingCompany',
            fields=[
                ('atoc_code', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
    ]
