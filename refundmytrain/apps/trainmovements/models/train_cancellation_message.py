from django.db import models

from refundmytrain.apps.naptan.models import NaptanRailStation
from refundmytrain.apps.operators.models import OperatingCompany

from refundmytrain.libs.rail_fields import (
    StanoxField, TrainMovementEventField, TrainIDField
)

from .train_entity import TrainEntity

from .message_id_mixin import MessageIDMixin
from .train_id_mixin import TrainIDMixin


class TrainCancellationMessage(MessageIDMixin, TrainIDMixin, models.Model):
    """
    Message type 2
    http://nrodwiki.rockshore.net/index.php/Train_Cancellation
    """

    train_entity = models.ForeignKey(TrainEntity)

    original_location_stanox = StanoxField(
        max_length=10,
        help_text=(
            'For an an "OUT OF PLAN" cancellation, this is the location that '
            'the train should have been at according to the schedule.'
        )
    )

    original_location_station = models.ForeignKey(
        NaptanRailStation,
        null=True,
        related_name='+',
    )

    original_location_timestamp = models.DateTimeField(
        help_text=(
            'For an "OUT OF PLAN" cancellation, this is the departure time '
            'of the location that the train should have been at according '
            'to the schedule'
        )
    )

    operating_company = models.ForeignKey(OperatingCompany)
    # division_code = models.ForeignKey(OperatingCompany)

    departure_timestamp = models.DateTimeField(
        help_text=(
            'The departure time at the location that the train is '
            'cancelled from (in milliseconds since the UNIX epoch)'
        )
    )

    location_stanox = models.CharField(
        max_length=10,
        help_text=(
            'The STANOX of the location that the train is being cancelled '
            'from. For an "OUT OF PLAN" cancellation, this STANOX will not '
            'be in the schedule, but a Train Movement message will have '
            'already been sent.'
        )
    )

    location = models.ForeignKey(NaptanRailStation)

    cancellaton_input_timestamp = models.DateTimeField(
        help_text=(
            'The time at which the cancellation was input to TRUST.'
        )
    )

    cancellaton_reason_code = models.CharField(
        max_length=10,
        help_text=(
            'The reason code for the cancellation, taken from the Delay '
            'Attribution Guide'
        )
    )

    cancellaton_type = models.CharField(
        max_length=10,
        help_text=(
            'Either "ON CALL" for a planned cancellation, "AT ORIGIN", '
            '"EN ROUTE" or "OUT OF PLAN"'
        )
    )

    train_service_code = models.CharField(
        max_length=10,
        help_text=(
            'Train service code as per the schedule.'
        )
    )

    train_file_address = models.CharField(
        max_length=10,
        help_text=(
            'The TOPS train file address, if applicable.'
        )
    )
