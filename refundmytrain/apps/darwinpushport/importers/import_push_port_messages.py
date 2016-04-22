# Example:
#
# <Pport xmlns="http://www.thalesgroup.com/rtti/PushPort/v12"
#        xmlns:ns3="http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2"
#        ts="2016-04-01T11:46:00.7543769+01:00" version="12.0">
#   <uR updateOrigin="Darwin">
#     <TS rid="201604010562730" ssd="2016-04-01" uid="G23691">
#       <ns3:LateReason>124</ns3:LateReason>
#       <ns3:Location pta="11:23" ptd="11:28" tpl="STOKEOT" wta="11:23"
#                     wtd="11:28">
#         <ns3:arr at="11:22" src="TD"/>
#         <ns3:dep delayed="true" et="11:46" src="Darwin"/>
#         <ns3:plat>1</ns3:plat>
#       </ns3:Location>
#       <ns3:Location tpl="STOKOTJ" wtp="11:29">
#         <ns3:pass delayed="true" et="11:47" src="Darwin"/>
#       </ns3:Location>
#       <ns3:Location pta="11:36" ptd="11:36" tpl="STONE" wta="11:35:30"
#                     wtd="11:36:30">
#         <ns3:arr delayed="true" et="11:53" src="Darwin"/>
#         <ns3:dep delayed="true" et="11:53" src="Darwin"/>
#         <ns3:plat>2</ns3:plat>
#       </ns3:Location>
#     </TS>
#   </uR>
# </Pport>

import logging

from django.db import transaction

from refundmytrain.apps.darwinpushport.models import (
    ActualArrival, OperatingCompany, Location, CallingPoint, TimetableJourney,
    NonPassengerJourney
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

IGNORED_IDS = None


def import_push_port_messages(f):
    global IGNORED_IDS
    IGNORED_IDS = set(
        j.rtti_train_id for j in NonPassengerJourney.objects.all())
    LOG.info('Ignoring {} rtti train ids'.format(len(IGNORED_IDS)))

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
    """
    A train status tag will have a number of subelements such as Location,
    LateReason etc:

    <TS rid="201604010562730" ssd="2016-04-01" uid="G23691">
      <ns3:LateReason>124</ns3:LateReason>
      <ns3:Location pta="11:23" ptd="11:28" tpl="STOKEOT" wta="11:23"
                    wtd="11:28">
        <ns3:arr at="11:22" src="TD"/>
        <ns3:dep delayed="true" et="11:46" src="Darwin"/>
        <ns3:plat>1</ns3:plat>
      </ns3:Location>
      <ns3:Location tpl="STOKOTJ" wtp="11:29">
        <ns3:pass delayed="true" et="11:47" src="Darwin"/>
      </ns3:Location>
      <ns3:Location pta="11:36" ptd="11:36" tpl="STONE" wta="11:35:30"
                    wtd="11:36:30">
        <ns3:arr delayed="true" et="11:53" src="Darwin"/>
        <ns3:dep delayed="true" et="11:53" src="Darwin"/>
        <ns3:plat>2</ns3:plat>
      </ns3:Location>
    </TS>
    """

    rtti_train_id = ts_element.attrib['rid']
    if rtti_train_id in IGNORED_IDS:
        return

    try:
        journey = TimetableJourney.objects.get(rtti_train_id=rtti_train_id)
    except TimetableJourney.DoesNotExist:
        LOG.warn("No such train {}, this shouldn't happen".format(
            rtti_train_id))
        return

    # start_date = ts_element.attrib['ssd']
    # uid = ts_element.attrib['uid']

    for sub in ts_element:
        full_tag = sub.tag

        if full_tag == LOCATION_TAG:
            handle_train_status_location(sub, journey)

        elif full_tag == LATE_REASON_TAG:
            handle_late_reason_tag(sub, journey)

        else:
            raise NotImplementedError(full_tag)


def handle_late_reason_tag(late_reason_tag, journey):
    journey.late_reason = late_reason_tag.text.strip()
    journey.save()


def handle_train_status_location(location_element, journey):
    tiploc = location_element.attrib['tpl']
    timetable_arrival_time = location_element.attrib.get('pta', None)
    # timetable_departure_time = location_element.attrib.get('ptd', None)

    minutes_late = set()

    for time_status in location_element:
        if 'at' not in time_status.attrib:
            continue

        if time_status.tag == ARRIVED_TAG:
            LOG.debug('{} actually arrived at {} {}'.format(
                journey.rtti_train_id, tiploc, time_status.attrib['at']))

            minutes_late.add(record_actual_arrival(
                journey, tiploc, time_status.attrib['at'],
                timetable_arrival_time
            ))

        elif time_status.tag == DEPARTED_TAG:
            LOG.debug('{} actually departed at {} {}'.format(
                journey.rtti_train_id, tiploc, time_status.attrib['at']))

        elif time_status.tag == PASS_TAG:
            pass

        else:
            LOG.warn('unhandled <{} at="{}"> for {} at {}'.format(
                time_status.tag,
                time_status.attrib['at'],
                journey.rtti_train_id,
                tiploc))

    if len(minutes_late):
        max_minutes_late = max(minutes_late)
        LOG.info('Train {} max delay is {} minutes'.format(
            journey.rtti_train_id, max_minutes_late))

        if max_minutes_late != journey.maximum_minutes_late:
            journey.maximum_minutes_late = max_minutes_late
            journey.save()


def record_actual_arrival(journey, tiploc, time, timetabled_time):

    kwargs = {
        'journey': journey,
        'location__tiploc': tiploc,
    }

    if timetabled_time is not None:
        kwargs['timetable_arrival_time'] = timetabled_time

    try:
        calling_point = CallingPoint.objects.get(**kwargs)

    except CallingPoint.DoesNotExist:
        # This could be because the train was a non-passenger journey.
        # TODO: look up how to make this quieter.
        LOG.warn('Failed to find CallingPoint({})'.format(kwargs))
        return 0

    else:
        if calling_point.timetable_arrival_time is None:
            return 0

        with transaction.atomic():
            ActualArrival.objects.filter(
                timetabled_calling_point=calling_point).delete()

            a = ActualArrival.objects.create(
                timetabled_calling_point=calling_point,
                time=time
            )
            return a.minutes_late()
