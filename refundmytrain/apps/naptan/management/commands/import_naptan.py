import json
import re

import batcher

from django.db import transaction
from django.core.management.base import BaseCommand

from refundmytrain.apps.naptan.models import NaptanRailStation


class Command(BaseCommand):
    help = ('Imports the NAPTAN data-set')

    def add_arguments(self, parser):
        parser.add_argument('naptan_json', type=str)

    def handle(self, *args, **options):
        with open(options['naptan_json'], 'r') as f, \
                batcher.batcher(NaptanRailStation.objects.bulk_create) as b, \
                transaction.atomic():

            NaptanRailStation.objects.all().delete()

            success_counter = 0
            unique_3_alphas = set()

            for record in json.load(f):

                obj = {
                    'tiploc': record['TiplocCode'],
                    'three_alpha': record['CrsCode'],
                    'name': self.strip_trailing_rail_station(
                        record['StationName']),
                }

                b.push(NaptanRailStation(**obj))
                success_counter += 1
                unique_3_alphas.add(obj['three_alpha'])

            self.stdout.write(self.style.SUCCESS(
                'Created {} locations with {} unique 3-alpha codes.'.format(
                    success_counter, len(unique_3_alphas))))

    @staticmethod
    def strip_trailing_rail_station(string):
        return re.sub('(.*) Rail Station$', r'\1', string)
