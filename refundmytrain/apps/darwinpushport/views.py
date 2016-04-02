from django.views.generic import DetailView, ListView
from .models import TimetableJourney


class TimetableJourneyList(ListView):
    model_name = TimetableJourney
    context_object_name = 'journeys'
    template_name = 'darwinpushport/timetable_journey_list.html'

    queryset = TimetableJourney.objects.all()[0:10]


class TimetableJourneyDetail(DetailView):
    model_name = TimetableJourney
    context_object_name = 'journey'
    template_name = 'darwinpushport/timetable_journey_detail.html'

    def get_queryset(self):
        return TimetableJourney.objects.filter(
            rtti_train_id=self.kwargs['pk']
        )
