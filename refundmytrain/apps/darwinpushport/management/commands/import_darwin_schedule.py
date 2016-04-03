import gzip

from django.core.management.base import BaseCommand

from refundmytrain.apps.darwinpushport.importers import import_schedule


class Command(BaseCommand):
    help = ('Imports a daily schedule file from National Rail Darwin')

    def add_arguments(self, parser):
        parser.add_argument('timetable_xml', type=str)

    def handle(self, *args, **options):

        filename = options['timetable_xml']
        if filename.endswith('.gz'):
            with gzip.open(filename, 'rb') as f:
                journies_created = import_schedule(f)
        else:
            with open(options['timetable_xml'], 'rb') as f:
                journies_created = import_schedule(f)

        self.stdout.write(self.style.SUCCESS(
            'Created {} journies.'.format(journies_created)))
