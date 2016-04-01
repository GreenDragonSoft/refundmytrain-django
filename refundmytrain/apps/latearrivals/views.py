from django.views.generic import ListView

from refundmytrain.apps.trainmovements.models import TrainMovementMessage


class ListLateArrivals(ListView):
    model = TrainMovementMessage
    template_name = 'latearrivals/late_arrivals.html'
    context_object_name = 'train_movement_messages'

    queryset = TrainMovementMessage.objects.filter(
        location_station__isnull=False,
        operating_company__isnull=False,
        variation_status='LATE',
        timetable_variation__gte=15,
    )
