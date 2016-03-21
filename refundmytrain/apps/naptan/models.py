from django.db import models


class NaptanRailStation(models.Model):

    # {
    #     "GridType": "U",
    #     "Easting": "335100",
    #     "TiplocCode": "LVRPLSH",
    #     "CrsCode": "LIV",
    #     "ModificationDateTime": "2006-09-18T18:24:34",
    #     "StationNameLang": "",
    #     "StationName": "Liverpool Lime Street Rail Station",
    #     "Modification": "rev",
    #     "AtcoCode": "9100LVRPLSH",
    #     "CreationDateTime": "2003-11-04T00:00:00",
    #     "RevisionNumber": "1",
    #     "Northing": "390500"
    # },

    def __str__(self):
        return '<NaptanRailStation "{}" ({})>'.format(
            self.name, self.three_alpha)

    tiploc = models.CharField(
        unique=True,  # Unlike in CORPUS, they are unique in NAPTAN
        max_length=50,
        help_text=('Timing Point Location - Codes relating to points used '
                   'in deriving train schedules. Loaded from field '
                   '`TiplocCode`')
    )

    three_alpha = models.CharField(
        unique=False,  # As in CORPUS, there are duplicates eg CLJ, WYB, WMB
        db_index=True,
        max_length=5,
        help_text=('A 3-character code used for stations. Previously '
                   'referred to as CRS (Computer Reservation System) or NRS '
                   '(National Reservation System) codes. Loaded from field '
                   '`CrsCode`')
    )

    name = models.CharField(
        db_index=True,
        max_length=256,
        help_text=('Station name, with `Rail Station` removed from the end. '
                   'Loaded from field `StationName`')
    )
