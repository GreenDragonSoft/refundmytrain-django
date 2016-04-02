from django.core.management.base import BaseCommand

from refundmytrain.apps.darwinpushport.importers import import_reference_data


class Command(BaseCommand):
    help = ('Imports the Network Rail CORPUS reference location data JSON file'
            'Entries without a 3-alpha or a STANOX are skipped.')

    def add_arguments(self, parser):
        parser.add_argument('reference_json', type=str)

    def handle(self, *args, **options):
        with open(options['reference_json'], 'rb') as f:
            locations_created, operating_companies_created = \
                    import_reference_data(f)

        self.stdout.write(self.style.SUCCESS(
            'Created {} locations, {} operating companies'.format(
                locations_created, operating_companies_created)))
