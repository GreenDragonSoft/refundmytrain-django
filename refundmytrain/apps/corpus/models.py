from django.db import models


class CorpusLocation(models.Model):
    # {
    #     "TIPLOC": " ",
    #     "UIC": " ",
    #     "NLCDESC16": "CAPRI HQ INPUT",
    #     "STANOX": " ",
    #     "NLC": "000900",
    #     "3ALPHA": " ",
    #     "NLCDESC": "AUTHORISED INPUT LOCATION 0009"
    #
    # },
    # NOTE: no idea what a UIC number is so omitting

    def __str__(self):
        return '<CorpusLocation desc="{}">'.format(self.nlc_description)

    tiploc = models.CharField(
        unique=True,  # Note that this implies a DB index
        null=True,
        blank=True,
        max_length=50,
        help_text=('Timing Point Location - Codes relating to points used '
                   'in deriving train schedules')
    )

    three_alpha = models.CharField(
        unique=False,  # For example ZBM appears twice
        db_index=True,
        null=True,
        blank=True,
        max_length=5,
        help_text=('A 3-character code used for stations. Previously '
                   'referred to as CRS (Computer Reservation System) or NRS '
                   '(National Reservation System) codes.')
    )

    stanox = models.CharField(
        unique=False,  # For example 70104 appears twice
        db_index=True,
        null=True,
        blank=True,
        max_length=10,
        help_text=('Station Number - these codes can refer to non-station '
                   'locations such as sidings and junctions. STANOX codes '
                   'are grouped by geographical area - the first two digits '
                   'specify the area in which the location exists.')
    )

    national_location_code = models.CharField(
        unique=True,  # Note that this implies a DB index
        null=True,
        blank=True,
        max_length=8,  # just in case they increase from 6!
        help_text=('(NLC) - A 6-digit code. These includes physical '
                   'locations such as stations and junctions as well as '
                   'codes relating to accounting and other purposes.')
    )

    nlc_description = models.CharField(
        null=True,
        blank=True,
        max_length=256,
        help_text='Description of the national location code (NLC)'
    )

    nlc_short_description = models.CharField(
        null=True,
        blank=True,
        max_length=16,
        help_text='16-char description of the national location code (NLC)'
    )
