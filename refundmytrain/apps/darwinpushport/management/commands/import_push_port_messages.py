import gzip

from django.core.management.base import BaseCommand

from refundmytrain.apps.darwinpushport.importers import (
    import_push_port_messages
)


class Command(BaseCommand):
    help = ('Imports a daily schedule file from National Rail Darwin')

    def add_arguments(self, parser):
        parser.add_argument('pushport_xml', type=str)

    def handle(self, *args, **options):
        filename = options['pushport_xml']

        if filename.endswith('.gz'):
            with gzip.open(filename, 'rb') as f:
                journies_created = import_push_port_messages(f)
        else:
            with open(filename, 'rb') as f:
                journies_created = import_push_port_messages(f)

        self.stdout.write(self.style.SUCCESS(
            'Created some journies.'.format(journies_created)))
