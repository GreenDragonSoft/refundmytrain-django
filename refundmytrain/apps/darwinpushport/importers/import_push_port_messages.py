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
import re

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

CALLING_POINT_PREFIX = (
    '{http://www.thalesgroup.com/rtti/PushPort/Schedules/v1}'
)

CALLING_POINT_TAGS = set([
    '{http://www.thalesgroup.com/rtti/PushPort/Schedules/v1}IP',
    '{http://www.thalesgroup.com/rtti/PushPort/Schedules/v1}PP',
    '{http://www.thalesgroup.com/rtti/PushPort/Schedules/v1}OR',
    '{http://www.thalesgroup.com/rtti/PushPort/Schedules/v1}DT',
    '{http://www.thalesgroup.com/rtti/PushPort/Schedules/v1}OPOR',
    '{http://www.thalesgroup.com/rtti/PushPort/Schedules/v1}OPIP',
])

SCHEDULE_CANCEL_REASON_TAG = (
    '{http://www.thalesgroup.com/rtti/PushPort/Schedules/v1}cancelReason'
)

IGNORED_IDS = None


class CantFindMatchingCallingPoint(Exception):
    pass


def import_push_port_messages(f):
    assert Location.objects.all().count()
    assert OperatingCompany.objects.all().count()

    global IGNORED_IDS
    IGNORED_IDS = set(
        j.rtti_train_id for j in NonPassengerJourney.objects.all())
    LOG.info('Ignoring {} rtti train ids'.format(len(IGNORED_IDS)))

    for xml_fragment in f.readlines():
        handle_xml_fragment(xml_fragment)


def handle_xml_fragment(xml_fragment):
    ur_element = parse_ur_element(xml_fragment)

    for element in ur_element:
        message_type = element.tag

        if message_type == TRAIN_STATUS_TAG:  # train status
            handle_train_status(element)

        elif message_type == SCHEDULE_TAG:
            handle_schedule(element)


def parse_ur_element(xml_string):
    root = etree.fromstring(xml_string)
    ur_element = root[0]

    assert UR_TAG == ur_element.tag, ur_element.tag
    return ur_element


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
    previous_late_reason = journey.late_reason
    new_late_reason = late_reason_tag.text.strip()

    if previous_late_reason != new_late_reason:
        journey.late_reason = new_late_reason
        journey.save()
        LOG.info('{} updated late reason from {} to {}'.format(
            journey.rtti_train_id, previous_late_reason, new_late_reason))


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

            try:
                minutes_late.add(record_actual_arrival(
                    journey, tiploc, time_status.attrib['at'],
                    timetable_arrival_time
                ))
            except CantFindMatchingCallingPoint:
                pass

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
        if max_minutes_late >= 30:
            LOG.info('{} max delay set to {} minutes'.format(
                journey.rtti_train_id, max_minutes_late))

        if max_minutes_late != journey.maximum_minutes_late:
            journey.maximum_minutes_late = max_minutes_late
            journey.save()


def record_actual_arrival(journey, tiploc, time, timetabled_time):
    """
    Return how late this arrival was, in minutes
    """

    kwargs = {
        'journey': journey,
        'location__tiploc': tiploc,
    }

    if timetabled_time is not None:
        kwargs['timetable_arrival_time'] = timetabled_time

    try:
        calling_point = CallingPoint.objects.get(**kwargs)

    except CallingPoint.DoesNotExist:
        # TODO: look up how to make this quieter.
        LOG.warn('Failed to find CallingPoint({})'.format(kwargs))
        raise CantFindMatchingCallingPoint

    except CallingPoint.MultipleObjectsReturned:
        LOG.warn('Multiple objects for CallingPoint({}). Currently cannot '
                 'disambiguate.'.format(kwargs))
        raise CantFindMatchingCallingPoint

    else:
        if calling_point.timetable_arrival_time is None:
            raise CantFindMatchingCallingPoint

        a, _ = ActualArrival.objects.update_or_create(
            timetabled_calling_point=calling_point,
            defaults={'time': time}
        )
        return a.minutes_late()


def handle_schedule(element):
    """
    <schedule rid="201604010576340" ssd="2016-04-01" toc="CH"
              trainId="2R03" uid="C91354">
      <ns2:OR act="TB" ptd="05:50" tpl="MARYLBN" wtd="05:50"/>
      <ns2:PP tpl="NEASDSJ" wtp="05:57"/>
      <ns2:IP act="T " pta="05:59" ptd="05:59" tpl="WEMBLSM"
              wta="05:58:30" wtd="05:59"/>
      <ns2:IP act="T " pta="06:04" ptd="06:04" tpl="NTHOLTP"
              wta="06:03:30" wtd="06:04"/>
      <ns2:PP tpl="NTHOPKJ" wtp="06:06"/>
      <ns2:IP act="T " pta="06:08" ptd="06:11" tpl="SRUISLP"
              wta="06:08" wtd="06:11"/>
      <ns2:DT act="TF" pta="06:17" tpl="WRUISLP" wta="06:15"/>
    </schedule>
    """
    journey = load_journey(element)
    if not journey:
        return

    three_alphas_before = set(filter(
        None,
        [cp.location.three_alpha for cp in journey.public_calling_points]
    ))

    journey.all_calling_points.all().delete()

    journey.all_calling_points.set(
        parse_calling_points(element, journey))

    three_alphas_after = set(filter(
        None,
        [cp.location.three_alpha for cp in journey.public_calling_points]
    ))

    journey.save()

    added = three_alphas_after - three_alphas_before
    removed = three_alphas_before - three_alphas_after

    if added or removed:
        LOG.info('{} updated schedule. added: "{}" removed "{}" '
                 '(public only)'.format(
                    journey.rtti_train_id,
                    ', '.join(added),
                    ', '.join(removed)))

    journey.add_from_to_entries()  # TODO: test that this actually works


def load_journey(element):

    if element.attrib.get('isPassengerSvc', None) == 'false':
        global IGNORED_IDS
        IGNORED_IDS.add(element.attrib['rid'])
        return None

    # TODO: filter out non-passenger services. See
    # http://nrodwiki.rockshore.net/index.php/Darwin:Schedule_Element
    # Look for isPassengerSvc="false"
    journey, was_created = TimetableJourney.objects.update_or_create(
        rtti_train_id=element.attrib['rid'],
        defaults={
            'start_date': element.attrib['ssd'],
            'operating_company': OperatingCompany.objects.get(
                atoc_code=element.attrib['toc']),
            'train_id': element.attrib['trainId'],
            'train_uid': element.attrib['uid'],
        }
    )
    return journey


def parse_calling_points(element, journey):
    """

    <uR requestID="0000000000000511" requestSource="at08" updateOrigin="CIS">
      <schedule rid="201604241274537" ssd="2016-04-24" toc="VT" trainCat="XX"
                trainId="1A09" uid="Y82072">
        <ns2:OR act="TB" ptd="09:38" tpl="LVRPLSH" wtd="09:38"/>
        <ns2:PP tpl="EDGH" wtp="09:42"/>
        <ns2:PP tpl="EDGHSB" wtp="09:42:30"/>
        <ns2:PP tpl="WVRTREJ" wtp="09:44"/>
        <ns2:PP tpl="ALERTN" wtp="09:46:30"/>
        <ns2:PP tpl="DITTON" wtp="09:50"/>
        <ns2:IP act="T " pta="09:53" ptd="09:54" tpl="RUNCORN" wta="09:52:30"
                wtd="09:54"/>
        <ns2:PP tpl="WEAVERJ" wtp="09:59"/>
        <ns2:PP tpl="ACBG" wtp="10:00"/>
      </schedule>
    </uR>
    """
    # TODO: factor out the repeated code between this function and the
    # ordinary schedule importer.

    for sub in element:
        if sub.tag == SCHEDULE_CANCEL_REASON_TAG:
            LOG.info('TODO: handle schedule cancel reason tag')
            continue

        assert sub.tag in CALLING_POINT_TAGS, '{} not in {}'.format(
            sub.tag, CALLING_POINT_TAGS)

        timetable_arrival_time = sub.attrib.get('pta', None)
        timetable_departure_time = sub.attrib.get('ptd', None)

        public_visible = (
            timetable_arrival_time is not None and
            timetable_departure_time is not None
        )
        tiploc = sub.attrib['tpl']
        calling_point_type = re.sub(CALLING_POINT_PREFIX, '', sub.tag)

        yield CallingPoint.objects.create(
            journey=journey,
            public_visible=public_visible,
            timetable_arrival_time=timetable_arrival_time,
            timetable_departure_time=timetable_departure_time,
            location=Location.objects.get(tiploc=tiploc),
            calling_point_type=calling_point_type
        )
