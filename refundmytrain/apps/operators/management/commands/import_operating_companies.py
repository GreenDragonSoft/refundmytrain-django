import json

import batcher

from django.db import transaction
from django.core.management.base import BaseCommand

from refundmytrain.apps.operators.models import OperatingCompany


class Command(BaseCommand):
    help = ('Imports the operating companies data-set')

    def add_arguments(self, parser):
        parser.add_argument('operators_json', type=str)

    def handle(self, *args, **options):
        with open(options['operators_json'], 'r') as f, \
                batcher.batcher(OperatingCompany.objects.bulk_create) as b, \
                transaction.atomic():

            OperatingCompany.objects.all().delete()

            success_counter = 0

            for record in json.load(f):
                record.pop('business_code')  # discard this, we don't need it

                b.push(OperatingCompany(**record))
                success_counter += 1

            self.stdout.write(self.style.SUCCESS(
                'Created {} operating companies.'.format(success_counter)))
