import datetime

from django.db.models import F

from django.views.generic import DetailView, ListView
from .models import TimetableJourney


class TimetableJourneyList(ListView):
    model_name = TimetableJourney
    context_object_name = 'journeys'
    template_name = 'darwinpushport/timetable_journey_list.html'

    def get_queryset(self):
        recent_journeys = TimetableJourney.objects.filter(
            start_date__lte=datetime.date.today(),
            start_date__gte=datetime.date.today() - datetime.timedelta(days=7)
        )

        recent_late_journeys = recent_journeys.filter(
            calling_points__actual_arrival_time__time__gte=(
                F('calling_points__timetable_arrival_time') +
                datetime.timedelta(minutes=30))
        ).distinct()

        return recent_late_journeys.order_by('start_date')


class TimetableJourneyDetail(DetailView):
    model_name = TimetableJourney
    context_object_name = 'journey'
    template_name = 'darwinpushport/timetable_journey_detail.html'

    def get_queryset(self):
        return TimetableJourney.objects.filter(
            rtti_train_id=self.kwargs['pk']
        )
