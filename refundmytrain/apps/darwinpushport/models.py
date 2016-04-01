from django.db import models


class OperatingCompany(models.Model):
    atoc_code = models.CharField(
        primary_key=True,
        max_length=2
    )

    name = models.CharField(max_length=256)

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
