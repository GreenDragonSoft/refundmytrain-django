import logging
import re

import batcher

from django.db import transaction

from refundmytrain.apps.darwinpushport.models import (
    OperatingCompany, Location, CancellationReason, LateRunningReason
)

from lxml import etree

LOG = logging.getLogger(__name__)

LATE_RUNNING_REASONS_TAG = (
    '{http://www.thalesgroup.com/rtti/XmlRefData/v3}LateRunningReasons'
)

CANCELLATION_REASONS_TAG = (
    '{http://www.thalesgroup.com/rtti/XmlRefData/v3}CancellationReasons'
)

LOCATION_REF_TAG = (
    '{http://www.thalesgroup.com/rtti/XmlRefData/v3}LocationRef'
)

TOC_REF_TAG = (
    '{http://www.thalesgroup.com/rtti/XmlRefData/v3}TocRef'
)


@transaction.atomic
def import_reference_data(f):
    locations_created = 0
    operating_companies_created = 0

    tree = etree.parse(f)
    root = tree.getroot()
    for element in root:
        if element.tag == LOCATION_REF_TAG:
            Location.objects.update_or_create(
                tiploc=element.attrib['tpl'],
                defaults={
                    'name': element.attrib['locname'],
                    'three_alpha': element.attrib.get('crs', None),
                }
            )
            locations_created += 1

        elif element.tag == TOC_REF_TAG:
            OperatingCompany.objects.update_or_create(
                atoc_code=element.attrib['toc'],
                defaults={
                    'name': element.attrib['tocname'],
                }
            )
            operating_companies_created += 1

        elif element.tag == LATE_RUNNING_REASONS_TAG:
            handle_late_running_reasons(element)

        elif element.tag == CANCELLATION_REASONS_TAG:
            handle_cancellation_reasons(element)

    return locations_created, operating_companies_created


def handle_late_running_reasons(reason_tags):
    """
    <LateRunningReasons>
      <Reason code="100" reasontext="This train has been delayed by a ..." />
      <Reason code="101" reasontext="This train has been delayed by a ..." />
    """

    count = 0
    with batcher.batcher(LateRunningReason.objects.bulk_create) as b:
        LateRunningReason.objects.all().delete()

        for reason_tag in reason_tags:
            b.push(LateRunningReason(
                code=reason_tag.attrib['code'],
                text=re.sub(
                    '^This train has been delayed by ',
                    '',
                    reason_tag.attrib['reasontext']),
            ))
            count += 1
    LOG.info('Created {} late runnning reasons'.format(count))


def handle_cancellation_reasons(reason_tags):
    """
    <CancellationReasons>
      <Reason code="100"
              reasontext="This train has been cancelled because of ..." />
      <Reason code="101"
              reasontext="This train has been cancelled because of ..." />
    """

    count = 0
    with batcher.batcher(CancellationReason.objects.bulk_create) as b:
        CancellationReason.objects.all().delete()

        for reason_tag in reason_tags:
            b.push(CancellationReason(
                code=reason_tag.attrib['code'],
                text=re.sub(
                    '^This train has been cancelled because of ',
                    '',
                    reason_tag.attrib['reasontext']),
            ))
            count += 1
    LOG.info('Created {} cancellation reasons'.format(count))
