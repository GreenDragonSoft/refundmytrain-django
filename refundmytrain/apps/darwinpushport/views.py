import datetime
import logging

from django.db.models import F

from django.views.generic import DetailView, ListView
from .models import TimetableJourney, JourneyFromTo

LOG = logging.getLogger(__name__)


class TimetableJourneyList(ListView):
    model = TimetableJourney
    context_object_name = 'journeys'
    template_name = 'darwinpushport/timetable_journey_list.html'

    def get_queryset(self):
        journeys = TimetableJourney.objects.filter(
            start_date__lte=datetime.date.today(),
            start_date__gte=datetime.date.today() - datetime.timedelta(days=7)
        )

        return journeys.order_by('start_date')[0:10]


class TimetableJourneyListFromTo(TimetableJourneyList):

    def get_queryset(self):
        from_three_alpha = self.kwargs['from'].upper()
        to_three_alpha = self.kwargs['to'].upper()

        try:
            return JourneyFromTo.objects.get(
                from_location__three_alpha=from_three_alpha,
                to_location__three_alpha=to_three_alpha,
            ).journeys.all().order_by('start_date')[0:10]
            # ^^ TODO, order by datetime of calling point they queried?
        except JourneyFromTo.DoesNotExist:
            return TimetableJourney.objects.none()


class TimetableJourneyDetail(DetailView):
    model_name = TimetableJourney
    context_object_name = 'journey'
    template_name = 'darwinpushport/timetable_journey_detail.html'

    def get_queryset(self):
        return TimetableJourney.objects.filter(
            rtti_train_id=self.kwargs['pk']
        )
