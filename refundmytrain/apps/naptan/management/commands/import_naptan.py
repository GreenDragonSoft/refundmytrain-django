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

            for record in json.load(f):

                obj = {
                    'tiploc': record['TiplocCode'],
                    'three_alpha': record['CrsCode'],
                    'name': self.strip_trailing_rail_station(
                        record['StationName']),
                }

                b.push(NaptanRailStation(**obj))
                success_counter += 1

            self.stdout.write(self.style.SUCCESS(
                'Created {} locations.'.format(
                    success_counter)))

    @staticmethod
    def strip_trailing_rail_station(string):
        return re.sub('(.*) Rail Station$', r'\1', string)
