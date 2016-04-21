import collections

from django.utils import timezone
from django.views.generic.base import TemplateView

from refundmytrain.apps.darwinpushport.models import ActualArrival

Result = collections.namedtuple('Result', 'summary,cls,text')


class StatusArrivals(TemplateView):
    template_name = 'status/status_arrivals.html'

    def get_context_data(self, *args, **kwargs):
        context = super(StatusArrivals, self).get_context_data(*args, **kwargs)

        context['result'] = get_arrivals_status()

        return context


def get_arrivals_status():
    most_recent_actual_arrival = ActualArrival.objects.all() \
            .order_by('-created_at').first()

    if not most_recent_actual_arrival:
        return Result(
            summary='ERROR',
            cls='error',
            text="No ActualArrivals found at all."
        )

    delta = timezone.now() - most_recent_actual_arrival.created_at

    return Result(
        summary='ERROR',
        cls='error',
        text="{}".format(str(delta))
    )
