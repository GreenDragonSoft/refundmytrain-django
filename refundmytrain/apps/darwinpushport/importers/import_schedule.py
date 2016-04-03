import re

import batcher

from django.db import transaction

from refundmytrain.apps.darwinpushport.models import (
    OperatingCompany, Location, TimetableJourney, CallingPoint
)

from lxml import etree

TAG_PATTERN = (r'{http://www.thalesgroup.com/rtti/XmlTimetable/v8}'
               '(?P<tag>[A-Za-z0-9]+)')
JOURNEY_TAG = r'{http://www.thalesgroup.com/rtti/XmlTimetable/v8}Journey'

CALLING_POINT_TAGS = list(CallingPoint.TYPE_CHOICES.keys())
CANCELLATION_TAG = 'cancelReason'


def import_schedule(f):
    assert Location.objects.all().count()
    assert OperatingCompany.objects.all().count()

    tree = etree.parse(f)
    root = tree.getroot()

    for element in root:
        if element.tag == JOURNEY_TAG:
            make_journey_with_calling_points(element)


def make_journey_with_calling_points(journey_element):
    with transaction.atomic():
        journey = make_journey(journey_element)

        if journey is None:
            return

        journey.calling_points.all().delete()

        with batcher.batcher(CallingPoint.objects.bulk_create) as b:
            for element in journey_element:

                if get_element_tag(element) in CALLING_POINT_TAGS:
                    make_calling_point(element, journey, b)

                elif get_element_tag(element) == CANCELLATION_TAG:
                    handle_cancellation_element(element, journey)

                else:
                    raise ValueError('Tag `{}` not in {}'.format(
                        get_element_tag(element), CALLING_POINT_TAGS))


def make_journey(element):
    assert 'Journey' == get_element_tag(element), (
        'Unexpected Journey tag: `{}`'.format(element.tag))

    if element.attrib.get('isPassengerSvc', None) == 'false':
        return  # Don't load commercial services

    journey, created = TimetableJourney.objects.get_or_create(
        rtti_train_id=element.attrib['rid'],
        defaults={
            'train_uid': element.attrib['uid'],
            'train_id': element.attrib['trainId'],
            'start_date': element.attrib['ssd'],
            'operating_company': OperatingCompany.objects.get(
                atoc_code=element.attrib['toc']),
        }
    )
    return journey


def parse_calling_point_element(element):
    """
    <OR tpl="DORKING" act="TB" plat="2" ptd="20:59" wtd="20:59" />
    <IP tpl="BOXHAWH" act="T " plat="1" pta="21:02" ptd="21:02" wta="21:01:30"
        wtd="21:02" />
    <IP tpl="LETHRHD" act="T " plat="1" pta="21:07" ptd="21:07" wta="21:06:30"
        wtd="21:07" />
    """

    timetable_arrival = element.attrib.get('pta', None)
    timetable_departure = element.attrib.get('ptd', None)
    location = Location.objects.get(
        tiploc=element.attrib['tpl'],
    )

    if timetable_departure is None and timetable_arrival is None:
        return None  # not helpful, discard

    # if location.three_alpha is None:
    #     return None  # not a public location

    return {
        'location': location,
        'calling_point_type': get_element_tag(element),
        'timetable_arrival_time': timetable_arrival,
        'timetable_departure_time': timetable_departure,
    }


def handle_cancellation_element(element, journey):
    journey.cancellation_reason = element.text
    journey.save()


def make_calling_point(element, journey, bulk_create_queue):

    calling_point_dict = parse_calling_point_element(element)

    if calling_point_dict is None:
        return

    bulk_create_queue.push(
        CallingPoint(
            journey=journey,
            **calling_point_dict
        )
    )


def get_element_tag(element):
    match = re.match(TAG_PATTERN, element.tag)

    if match is None:
        raise ValueError("Tag doesn't match expected format: `{}`, "
                         "format: {}".format(element.tag, TAG_PATTERN))
    return match.group('tag')
