"""
Objective: From a STANOX, find exactly 1 NAPTAN rail entry
           (three-alpha + name), for example "Liverpool Lime Street (LIV)"

The NAPTAN data does not have not a STANOX field so we must use the CORPUS
data, joining on the tiploc and 3-alpha fields:

    STANOX --> CORPUS --> NAPTAN
               tiploc     tiploc
               3-alpha    3-alpha

Caveats:
    - Not every STANOX code refers to a NAPTAN station

But since we don't know the STANOX codes in advance, we have to:
  -

Test of success:
    - There should be a link to a STANOX for every unique 3-alpha
    - Each STANOX should resolve to exactly one 3-alpha

"""

import batcher

from django.db import transaction
from django.core.management.base import BaseCommand

from refundmytrain.apps.corpus.models import CorpusLocation
from refundmytrain.apps.naptan.models import NaptanRailStation
from refundmytrain.apps.corpus_naptan_link.models import CorpusNaptanLink

TIPLOC_CORRECTIONS = {
    'BERMPRK': 'BERMPK'  # NAPTAN incorrectly has BERMPK
}

IGNORE_NATPAN_3_ALPHAS = set([
    'HTR',  # HEATHROW CENTRAL BUS STN
    'SHV',  # SOUTHSEA HOVERPORT
    'FRR',  # Frosterley Rail Station - disused
    'HWF',  # HEATHROW TERMINAL 4 BUS
    'HWX',  # HEATHROW AIRPORT T5 (BUS)
    'LEB',  # Lea Bridge: does not appear to have a STANOX in the Corpus
    'PMG',  # No idea, can't find any reference
    'RBU',  # READING BUS
    'STQ',  # SOUTHAMPTON TOWN QUAY (it's a marina)
    'TYB',  # No idea, can't find any reference
    'WLH',  # No idea, can't find any reference
])


class Command(BaseCommand):
    help = ('Uses the CORPUS data to create a search from STANOX code to '
            'a NaptanRailStation entry.')

    # def add_arguments(self, parser):
    #     parser.add_argument('corpus_json', type=str)

    def handle(self, *args, **options):

        all_stanox_codes = set(filter(
            None,
            (x.stanox for x in CorpusLocation.objects.all())
        ))

        unique_3_alphas = set(filter(
            None,
            (x.three_alpha for x in NaptanRailStation.objects.all())
        )) - IGNORE_NATPAN_3_ALPHAS

        self.stdout.write('Got {} unique STANOX codes'.format(
            len(all_stanox_codes)))
        self.stdout.write('Got {} unique 3-alphas from NAPTAN'.format(
            len(unique_3_alphas)))

        counter = 0
        flag_count = 0

        with transaction.atomic(), \
                batcher.batcher(CorpusNaptanLink.objects.bulk_create) as b:

            CorpusNaptanLink.objects.all().delete()

            for corpus_location in CorpusLocation.objects.filter(
                    stanox__isnull=False,
                    tiploc__isnull=False):

                search_tiploc = TIPLOC_CORRECTIONS.get(
                    corpus_location.tiploc,
                    corpus_location.tiploc)

                try:
                    naptan_rail_station = NaptanRailStation.objects.get(
                        tiploc=search_tiploc)
                except NaptanRailStation.DoesNotExist:
                    pass

                else:

                    if (corpus_location.three_alpha !=
                            naptan_rail_station.three_alpha):
                        flag_warning = "3-alphas don't match"
                        flag_count += 1
                    else:
                        flag_warning = None

                    b.push(CorpusNaptanLink(
                        corpus_location=corpus_location,
                        naptan_rail_station=naptan_rail_station,
                        flag_warning=flag_warning,
                    ))

                    counter += 1

        self.stdout.write(self.style.SUCCESS(
            'Matched {} out of {} STANOX -> NAPTAN rail stations.'.format(
                counter, len(all_stanox_codes))))
        self.stdout.write(self.style.WARNING(
            '{} warnings.'.format(flag_count)))

        linked_3_alphas = set(x.naptan_rail_station.three_alpha
                              for x in CorpusNaptanLink.objects.all())

        missing_3_alphas = sorted(unique_3_alphas - linked_3_alphas)
        self.stdout.write(self.style.ERROR(
            "These 3-alphas aren't linked to from any corpus entry: {}".format(
                ', '.join(missing_3_alphas))))
