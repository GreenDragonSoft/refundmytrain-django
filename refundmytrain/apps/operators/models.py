from django.db import models


class OperatingCompany(models.Model):
    numeric_code = models.CharField(
        # These are not unique, for example 88 points to:
        # - Govia Thameslink Railway (Great Northern) (atoc GN)
        # - Govia Thameslink Railway (Thameslink) (atox TL)
        max_length=2,
        db_index=True,
    )

    atoc_code = models.CharField(
        # These are not unique, for example London Underground (LU) links to
        # multiple numeric codes...
        max_length=2,
        db_index=True,
    )

    name = models.CharField(
        max_length=256,
        db_index=True,
    )

    def __str__(self):
        return '{} ({})'.format(self.name, self.atoc_code)
