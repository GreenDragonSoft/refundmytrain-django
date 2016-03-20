import json


from django.core.management.base import BaseCommand, CommandError
from refundmytrain.apps.corpus.models import CorpusLocation


class Command(BaseCommand):
    help = ('Imports the Network Rail CORPUS reference location data JSON file'
            'Entries without a 3-alpha or a STANOX are skipped.')

    def add_arguments(self, parser):
        parser.add_argument('corpus_json', type=str)

    def handle(self, *args, **options):
        with open(options['corpus_json'], 'r') as f:
            CorpusLocation.objects.all().delete()

            success_counter = 0
            skip_counter = 0

            for record in json.load(f)['TIPLOCDATA']:

                obj = {
                    'tiploc': self.parse_field(
                        record['TIPLOC']),
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

                if obj['three_alpha'] is None or obj['stanox'] is None:
                    skip_counter += 1
                    # self.stdout.write(self.style.WARNING(
                    #     'Skipping location without 3-alpha'))
                    continue  # Skip any non-stations for now.

                obj, created = CorpusLocation.objects.update_or_create(
                        stanox=obj.pop('stanox'), defaults=obj)

                success_counter += 1

            self.stdout.write(self.style.SUCCESS(
                'Created {} locations (having 3-alpha and STANOX)'.format(
                    success_counter)))

            self.stdout.write(self.style.WARNING(
                'Skipped {} locations (missing 3-alpha/STANOX)'.format(
                    skip_counter)))

    @staticmethod
    def parse_field(string):
        if string.strip() == '':
            return None
        return string
