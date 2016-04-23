import datetime
import logging

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from django.views.generic import DetailView, ListView, TemplateView
from .models import TimetableJourney, JourneyFromTo, CallingPoint

LOG = logging.getLogger(__name__)


class TimetableJourneyList(ListView):
    model = TimetableJourney
    context_object_name = 'journeys'
    template_name = 'darwinpushport/timetable_journey_list.html'

    def get_queryset(self):
        journeys = TimetableJourney.objects.filter(
            start_date__lte=datetime.date.today(),
            start_date__gte=datetime.date.today() - datetime.timedelta(days=7),
            maximum_minutes_late__gte=30,
        )

        return journeys.order_by('-rtti_train_id')[0:20]


class TimetableJourneyListFromTo(TemplateView):
    template_name = 'darwinpushport/journey_from_to_list.html'
    context_object_name = 'date_journey_groups'

    def get_context_data(self, *args, **kwargs):
        context = super(TimetableJourneyListFromTo, self).get_context_data(
            *args, **kwargs)

        from_three_alpha = self.kwargs['from'].upper()
        to_three_alpha = self.kwargs['to'].upper()

        journey_from_to = get_object_or_404(
            JourneyFromTo,
            from_location__three_alpha=from_three_alpha,
            to_location__three_alpha=to_three_alpha,
        )

        journeys = journey_from_to.journeys.prefetch_related(
            'all_calling_points').order_by('start_date')

        context['journeys_by_date'] = self._get_grouped_journeys(
            journeys, from_three_alpha, to_three_alpha)
        context['from_name'] = journey_from_to.from_location.name
        context['to_name'] = journey_from_to.to_location.name

        return context

    @staticmethod
    def _get_grouped_journeys(journeys, from_three_alpha, to_three_alpha):
        for date in sorted(set(j.start_date for j in journeys), reverse=True):
            journeys_for_date = []

            for journey in filter(lambda j: j.start_date == date, journeys):
                calling_points = list(journey.public_calling_points)

                def find_calling_point(three_alpha):
                    return next(filter(
                        lambda cp: cp.location.three_alpha == three_alpha,
                        calling_points
                    ))

                journeys_for_date.append({
                    'journey_rtti_train_id': journey.rtti_train_id,
                    'from_calling_point': find_calling_point(from_three_alpha),
                    'to_calling_point': find_calling_point(to_three_alpha),
                    'operating_company': journey.operating_company,
                    'start_location': calling_points[0].location,
                    'end_location': calling_points[-1].location,
                })

            yield (date, sorted(
                journeys_for_date,
                key=lambda x: x['from_calling_point'].timetable_departure_time)
            )


class TimetableJourneyDetail(DetailView):
    model_name = TimetableJourney
    context_object_name = 'journey'
    template_name = 'darwinpushport/timetable_journey_detail.html'

    def get_queryset(self):
        return TimetableJourney.objects.filter(
            rtti_train_id=self.kwargs['pk']
        )
