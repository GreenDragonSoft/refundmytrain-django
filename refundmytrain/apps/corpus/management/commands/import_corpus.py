import batcher

import json

from django.db import transaction
from django.core.management.base import BaseCommand

from refundmytrain.apps.corpus.models import CorpusLocation


class Command(BaseCommand):
    help = ('Imports the Network Rail CORPUS reference location data JSON file'
            'Entries without a 3-alpha or a STANOX are skipped.')

    def add_arguments(self, parser):
        parser.add_argument('corpus_json', type=str)

    def handle(self, *args, **options):
        with open(options['corpus_json'], 'r') as f, \
                batcher.batcher(CorpusLocation.objects.bulk_create) as b, \
                transaction.atomic():

            CorpusLocation.objects.all().delete()

            success_counter = 0

            for record in json.load(f)['TIPLOCDATA']:

                obj = {
                    'tiploc': self.parse_field(
                        record['TIPLOC']),
                    'uic_code': self.parse_field(
                        record['UIC']),
                    'three_alpha': self.parse_field(
                        record['3ALPHA']),
                    'stanox': self.parse_field(
                        record['STANOX']),
                    'national_location_code': self.parse_field(
                        record['NLC']),
                    'nlc_description': self.parse_field(
                        record['NLCDESC']),
                    'nlc_short_description': self.parse_field(
                        record['NLCDESC16'])
                }

                b.push(CorpusLocation(**obj))
                success_counter += 1

            self.stdout.write(self.style.SUCCESS(
                'Created {} locations.'.format(
                    success_counter)))

    @staticmethod
    def parse_field(string):
        if string.strip() == '':
            return None
        return string
