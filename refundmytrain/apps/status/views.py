import collections

from django.views.generic.base import TemplateView
from django.utils import timezone
from django.template.response import TemplateResponse

from refundmytrain.apps.darwinpushport.models import (
    ActualArrival, CallingPoint, TimetableJourney, NonPassengerJourney,
    ImportLog, JourneyFromTo, Location
)

StatusCheck = collections.namedtuple('StatusCheck', 'name,result')
Result = collections.namedtuple('Result', 'summary,cls,text')


class TemplateResponseServerError(TemplateResponse):
        status_code = 500


class StatusIndex(TemplateView):
    template_name = 'status/status_index.html'

    def get_context_data(self):
        all_calling_points = CallingPoint.objects.all()
        latest_import_log = get_latest_import_log()
        latest_actual_arrival = get_latest_actual_arrival()

        alerts = []

        if longer_ago_than(60, latest_import_log.import_datetime):
            alerts.append('Latest import log was >1 hour ago.')

        if longer_ago_than(20, latest_actual_arrival.created_at):
            alerts.append('Latest ActualArrival was created >20 minutes ago.')

        if longer_ago_than(120, latest_actual_arrival.to_datetime()):
            alerts.append('Latest ActualArrival train arrival time was >2 '
                          'hour ago')
        if alerts:
            self.response_class = TemplateResponseServerError
        else:
            self.response_class = TemplateResponse

        return {
            'alerts': alerts,

            'num_journeys': TimetableJourney.objects.all().count(),
            'earliest_journey':
                get_earliest_journey(),

            'latest_journey':
                get_latest_journey(),

            'num_non_passenger_journeys':
                NonPassengerJourney.objects.all().count(),

            'num_calling_points': all_calling_points.count(),

            'num_calling_points_timetable_arrival':
                all_calling_points.filter(
                    timetable_arrival_time__isnull=False).count(),

            'num_calling_points_public_visible':
                all_calling_points.filter(
                    public_visible=True).count(),

            'num_actual_arrivals': ActualArrival.objects.all().count(),
            'latest_actual_arrival': latest_actual_arrival,
            'num_import_logs': ImportLog.objects.all().count(),
            'latest_import_log': latest_import_log,
            'num_journey_from_tos': JourneyFromTo.objects.all().count(),
            'num_locations': Location.objects.all().count(),
            'num_locations_with_three_alpha': Location.objects.filter(
                three_alpha__isnull=False).count(),
        }


def longer_ago_than(minutes, dt):
    return (timezone.now() - dt).total_seconds() / 60 > minutes


def get_earliest_journey():
    return TimetableJourney.objects.all() \
            .order_by('start_date').first()


def get_latest_journey():
    return TimetableJourney.objects.all() \
            .order_by('start_date').last()


def get_latest_actual_arrival():
    return ActualArrival.objects.all() \
            .order_by('-created_at').first()


def get_latest_import_log():
    return ImportLog.objects.all() \
            .order_by('-import_datetime').first()
