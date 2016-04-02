import batcher

from django.db import transaction

from refundmytrain.apps.darwinpushport.models import OperatingCompany, Location

from lxml import etree


def import_reference_data(f):
    locations_created = 0
    operating_companies_created = 0

    with batcher.batcher(Location.objects.bulk_create) as location_b, \
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

    return locations_created, operating_companies_created
