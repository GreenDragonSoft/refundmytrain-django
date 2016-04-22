import itertools
import logging

from collections import defaultdict

import batcher

from django.db import transaction

from refundmytrain.apps.darwinpushport.models import (
    OperatingCompany, Location, TimetableJourney, CallingPoint, JourneyFromTo,
    NonPassengerJourney
)

from lxml import etree

LOG = logging.getLogger(__name__)

TAG_PATTERN = (r'{http://www.thalesgroup.com/rtti/XmlTimetable/v8}'
               '(?P<tag>[A-Za-z0-9]+)')
JOURNEY_TAG = r'{http://www.thalesgroup.com/rtti/XmlTimetable/v8}Journey'

CALLING_POINT_TAGS = list(CallingPoint.TYPE_CHOICES.keys())
CANCELLATION_TAG = 'cancelReason'

LOG_EVERY = 500


def import_schedule(f):
    assert Location.objects.all().count()
    assert OperatingCompany.objects.all().count()

    journey_cache = {}

    def _save_non_passenger_service_ids():
        bulk_add_non_passenger_service_ids(
            set(get_non_passenger_service_ids(f)))

    def _create_new_journeys(journey_cache):
        existing_journey_ids = get_existing_journey_ids()

        LOG.info('Attempting to load {} journeys. Database contains {} '
                 'existing journeys'.format(
                     sum(1 for _ in get_journey_elements(f)),
                     len(existing_journey_ids)))

        for journey in bulk_create_new_journeys(
                get_journey_elements(f), existing_journey_ids):
            journey_cache[journey.rtti_train_id] = journey

        LOG.info('Bulk created {} new journeys.'.format(len(journey_cache)))

    def _load_remaining_journeys(journey_cache):
        for journey in load_existing_journeys(get_journey_elements(f)):
            journey_cache[journey.rtti_train_id] = journey

        LOG.info('Cache now contains {} journeys.'.format(len(journey_cache)))
        assert None not in set(journey_cache.values())

    def _delete_existing_calling_points(journeys):
        count = 0
        total = len(journeys)

        for journey in journeys:
            journey.all_calling_points.all().delete()
            count += 1
            if count % LOG_EVERY == 0:
                LOG.info('Deleted calling points for {} / {} journeys'.format(
                    count, total))

    def _insert_calling_points(journey_cache):
        from_to_entries = defaultdict(list)

        for (loc_from, loc_to), journey in bulk_insert_calling_points(
                get_journey_elements(f), journey_cache):
            from_to_entries[(loc_from, loc_to)].append(journey)
        return from_to_entries

    def _update_journey_from_tos(from_to_entries):
        LOG.info('Updating {} JourneyFromTo entries.'.format(
            len(from_to_entries)))

        update_search_entries(from_to_entries)

    with transaction.atomic():
        _save_non_passenger_service_ids()
        _create_new_journeys(journey_cache)
        _load_remaining_journeys(journey_cache)
        _delete_existing_calling_points(journey_cache.values())
        new_from_to_entries = _insert_calling_points(journey_cache)

    del journey_cache
    _update_journey_from_tos(new_from_to_entries)


def is_passenger_service(element):
    """
    Commercial (non-passenger) services have isPassengerSvc="false".
    Passenger services don't have this attribute at all (yuk)
    """
    try:
        value = element.attrib['isPassengerSvc']
    except KeyError:
        return True  # attribute missing means it IS a passenger service
    else:
        assert value == 'false', value
        return False


def get_journey_elements(f):
    """
    Yield lxml <Journey> element for all passenger services.
    """
    return filter(is_passenger_service, get_all_journey_elements(f))


def get_non_passenger_service_ids(f):
    """
    Yield rtti_train_ids for every non-passenger service, eg commercial ones
    """

    for element in get_all_journey_elements(f):
        if not is_passenger_service(element):
            yield element.attrib['rid']


def get_all_journey_elements(f):
    f.seek(0)

    for xml_chunk in split_into_journey_chunks(f):
        element = etree.fromstring(xml_chunk)

        assert 'Journey' == get_element_tag(element), (
            'Unexpected Journey tag: `{}`'.format(element.tag))

        yield element


def get_existing_journey_ids():
    return set(j.rtti_train_id for j in TimetableJourney.objects.all())


def bulk_add_non_passenger_service_ids(rtti_train_ids_set):
    # ~ 11K passenger ids per schedule

    existing_ids = set(
        j.rtti_train_id for j in NonPassengerJourney.objects.all()
    )

    ids_to_add = rtti_train_ids_set - existing_ids

    count = 0
    total = len(ids_to_add)

    with batcher.batcher(NonPassengerJourney.objects.bulk_create) as b:
        for rtti_train_id in ids_to_add:
            b.push(NonPassengerJourney(rtti_train_id=rtti_train_id))
            count += 1

            if count % LOG_EVERY == 0:
                LOG.info('Created {} / {} NonPassengerJourneys'.format(
                    count, total))


def bulk_create_new_journeys(journey_elements, ignore_rtti_ids):

    with batcher.batcher(TimetableJourney.objects.bulk_create) as b:
        for element in journey_elements:

            if element.attrib['rid'] in ignore_rtti_ids:
                continue

            journey = TimetableJourney(**{
                'rtti_train_id': element.attrib['rid'],
                'train_uid': element.attrib['uid'],
                'train_id': element.attrib['trainId'],
                'start_date': element.attrib['ssd'],
                'operating_company': OperatingCompany.objects.get(
                    atoc_code=element.attrib['toc']),  # TODO: cache
            })
            b.push(journey)
            yield journey


def load_existing_journeys(journey_elements):
    for element in journey_elements:
        yield TimetableJourney.objects.get(
            rtti_train_id=element.attrib['rid'])


def split_into_journey_chunks(f):
    """
    Parse through the file, yielding strings containing XML like this:
      <Journey ...>
      ...
      </Journey>
    """
    chunk_lines = []
    currently_mid_tag = False

    for line in (line.decode('utf-8') for line in f.readlines()):
        if line.lstrip().startswith('<Journey'):
            currently_mid_tag = True

        if currently_mid_tag:
            chunk_lines.append(line)

        if line.lstrip().startswith('</Journey'):
            yield ''.join(chunk_lines).encode('utf-8')
            chunk_lines = []
            currently_mid_tag = False


def bulk_insert_calling_points(journey_elements, journey_cache):
    """
    Attach calling points for journeys and yield JourneyFromTo search entries
    like (('LIV', 'MAN'), Journey)
    """

    location_cache = {l.tiploc: l for l in Location.objects.all()}

    journey_count = 0

    with batcher.batcher(CallingPoint.objects.bulk_create) as b:
        for journey_element in journey_elements:
            journey = journey_cache[journey_element.attrib['rid']]
            calling_points = []

            for element in journey_element:
                if get_element_tag(element) in CALLING_POINT_TAGS:
                    calling_point = make_calling_point(
                        element, journey, location_cache)

                    calling_points.append(calling_point)

            for calling_point in calling_points:
                b.push(calling_point)

            public_calling_points = filter(
                lambda cp: cp.public_visible, calling_points)

            for from_cp, to_cp in itertools.combinations(
                    public_calling_points, 2):
                yield ((from_cp.location, to_cp.location), journey)

            journey_count += 1

            if journey_count % LOG_EVERY == 0:
                LOG.info('Added CallingPoints for {} journeys'.format(
                    journey_count))


def make_calling_point(element, journey, location_cache):
    """
    <OR tpl="DORKING" act="TB" plat="2" ptd="20:59" wtd="20:59" />
    <IP tpl="BOXHAWH" act="T " plat="1" pta="21:02" ptd="21:02" wta="21:01:30"
        wtd="21:02" />
    <IP tpl="LETHRHD" act="T " plat="1" pta="21:07" ptd="21:07" wta="21:06:30"
        wtd="21:07" />
    """

    timetable_arrival = element.attrib.get('pta', None)
    timetable_departure = element.attrib.get('ptd', None)
    location = location_cache[element.attrib['tpl']]

    if timetable_departure is None and timetable_arrival is None:
        public_visible = False
    else:
        public_visible = True

    return CallingPoint(**{
        'journey': journey,
        'public_visible': public_visible,
        'location': location,
        'calling_point_type': get_element_tag(element),
        'timetable_arrival_time': timetable_arrival,
        'timetable_departure_time': timetable_departure,
    })


def handle_cancellation_element(element, journey):
    journey.cancellation_reason = element.text
    journey.save()


def get_element_tag(element):
    # match = re.match(TAG_PATTERN, element.tag)

    # if match is None:
    #     raise ValueError("Tag doesn't match expected format: `{}`, "
    #                      "format: {}".format(element.tag, TAG_PATTERN))
    # return match.group('tag')
    return element.tag


def update_search_entries(journey_from_tos):
    count = 0
    total = len(journey_from_tos)

    for (from_location, to_location), journeys in journey_from_tos.items():
        obj, _ = JourneyFromTo.objects.get_or_create(
            from_location=from_location,
            to_location=to_location,
        )

        existing_journeys = set(obj.journeys.all())
        existing_journeys.update(set(journeys))

        obj.journeys.set(existing_journeys)

        count += 1
        if count % LOG_EVERY == 0:
            LOG.info('Updated {} / {} JourneyFromTo entries'.format(
                count, total))
