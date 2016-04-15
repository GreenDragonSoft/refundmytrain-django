import logging

from django.db import transaction

from refundmytrain.apps.darwinpushport.models import (
    ActualArrival, OperatingCompany, Location, CallingPoint
)

from lxml import etree

LOG = logging.getLogger(__name__)

UR_TAG = '{http://www.thalesgroup.com/rtti/PushPort/v12}uR'

DEACTIVATED_TAG = '{http://www.thalesgroup.com/rtti/PushPort/v12}deactivated'
SCHEDULE_TAG = '{http://www.thalesgroup.com/rtti/PushPort/v12}schedule'
TRAIN_STATUS_TAG = '{http://www.thalesgroup.com/rtti/PushPort/v12}TS'

LOCATION_TAG = (
    '{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}Location'
)

LATE_REASON_TAG = (
    '{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}LateReason'
)


'{http://www.thalesgroup.com/rtti/PushPoctualrt/Forecasts/v2}Location'

ARRIVED_TAG = (
    '{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}arr'
)

DEPARTED_TAG = (
    '{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}dep'
)

PASS_TAG = (
    '{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}pass'
)


def import_push_port_messages(f):
    for xml_fragment in f.readlines():
        load_journies_from_xml_file(xml_fragment)


def load_journies_from_xml_file(xml_string):
    assert Location.objects.all().count()
    assert OperatingCompany.objects.all().count()

    root = etree.fromstring(xml_string)
    ur_element = root[0]

    assert UR_TAG == ur_element.tag, ur_element.tag

    for element in ur_element:
        message_type = element.tag

        if message_type == TRAIN_STATUS_TAG:  # train status
            handle_train_status(element)

        # else:
        #     stdout.write('Not implemented: {}'.format(message_type))


def handle_train_status(ts_element):
    rtti_train_id = ts_element.attrib['rid']
    # start_date = ts_element.attrib['ssd']
    # uid = ts_element.attrib['uid']

    for sub in ts_element:
        full_tag = sub.tag

        if full_tag == LOCATION_TAG:
            handle_train_status_location(sub, rtti_train_id)

        elif full_tag == LATE_REASON_TAG:
            pass

        else:
            raise NotImplementedError(full_tag)


def handle_train_status_location(location_element, rtti_train_id):
    tiploc = location_element.attrib['tpl']
    timetable_arrival_time = location_element.attrib.get('pta', None)
    # timetable_departure_time = location_element.attrib.get('ptd', None)

    for time_status in location_element:
        if 'at' not in time_status.attrib:
            continue

        if time_status.tag == ARRIVED_TAG:
            LOG.debug('{} actually arrived at {} {}'.format(
                rtti_train_id, tiploc, time_status.attrib['at']))

            record_actual_arrival(
                rtti_train_id, tiploc, time_status.attrib['at'],
                timetable_arrival_time
            )

        elif time_status.tag == DEPARTED_TAG:
            LOG.debug('{} actually departed at {} {}'.format(
                rtti_train_id, tiploc, time_status.attrib['at']))

        elif time_status.tag == PASS_TAG:
            pass

        else:
            LOG.warn('unhandled <{} at="{}"> for {} at {}'.format(
                time_status.tag,
                time_status.attrib['at'],
                rtti_train_id,
                tiploc))


def record_actual_arrival(rtti_train_id, tiploc, time, timetabled_time):

    kwargs = {
        'journey__rtti_train_id': rtti_train_id,
        'location__tiploc': tiploc,
    }

    if timetabled_time is not None:
        kwargs['timetable_arrival_time'] = timetabled_time

    try:
        calling_point = CallingPoint.objects.get(**kwargs)

    except CallingPoint.DoesNotExist:
        # This could be because the train was a non-passenger journey.
        # TODO: look up how to make this quieter.
        LOG.info('Failed to find CallingPoint({})'.format(kwargs))

    else:

        with transaction.atomic():
            ActualArrival.objects.filter(
                timetabled_calling_point=calling_point).delete()

            ActualArrival.objects.create(
                timetabled_calling_point=calling_point,
                time=time
            )
