import batcher

import json

from django.db import transaction
from django.core.management.base import BaseCommand

from refundmytrain.apps.darwinpushport.models import OperatingCompany, Location

from lxml import etree


class Command(BaseCommand):
    help = ('Imports the Network Rail CORPUS reference location data JSON file'
            'Entries without a 3-alpha or a STANOX are skipped.')

    def add_arguments(self, parser):
        parser.add_argument('reference_json', type=str)

    def handle(self, *args, **options):
        locations_created = 0
        operating_companies_created = 0

        with open(options['reference_json'], 'rb') as f, \
                batcher.batcher(Location.objects.bulk_create) as location_b, \
                batcher.batcher(OperatingCompany.objects.bulk_create) as operator_b, \
                transaction.atomic():

            Location.objects.all().delete()
            OperatingCompany.objects.all().delete()

            tree = etree.parse(f)
            root = tree.getroot()
            for element in root:
                if element.tag == '{http://www.thalesgroup.com/rtti/XmlRefData/v3}LocationRef':
                    location_b.push(
                        Location(
                            tiploc=element.attrib['tpl'],
                            name=element.attrib['locname'],
                            three_alpha=element.attrib.get('crs', None),
                        )
                    )
                    locations_created += 1

                elif element.tag == '{http://www.thalesgroup.com/rtti/XmlRefData/v3}TocRef':
                    operator_b.push(
                        OperatingCompany(
                            atoc_code=element.attrib['toc'],
                            name=element.attrib['tocname'],
                        )
                    )
                    operating_companies_created += 1

        self.stdout.write(self.style.SUCCESS(
            'Created {} locations, {} operating companies'.format(
                locations_created, operating_companies_created)))
