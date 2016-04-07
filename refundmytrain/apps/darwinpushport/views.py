import datetime
import logging

from django.db.models import F

from django.views.generic import DetailView, ListView
from .models import TimetableJourney

LOG = logging.getLogger(__name__)


class TimetableJourneyList(ListView):
    model_name = TimetableJourney
    context_object_name = 'journeys'
    template_name = 'darwinpushport/timetable_journey_list.html'

    def get_queryset(self):
        recent_journeys = TimetableJourney.objects.filter(
            start_date__lte=datetime.date.today(),
            start_date__gte=datetime.date.today() - datetime.timedelta(days=7)
        )

        LOG.info('{} recent journeys'.format(recent_journeys.count()))

        recent_late_journeys = recent_journeys.filter(
                calling_points__actual_arrival_time__isnull=False).distinct()

        return recent_late_journeys.order_by('start_date')[0:10]


class TimetableJourneyDetail(DetailView):
    model_name = TimetableJourney
    context_object_name = 'journey'
    template_name = 'darwinpushport/timetable_journey_detail.html'

    def get_queryset(self):
        return TimetableJourney.objects.filter(
            rtti_train_id=self.kwargs['pk']
        )
