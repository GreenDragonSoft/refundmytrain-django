from django.db import models

# from refundmytrain.apps.naptan.models import NaptanRailStation
# from refundmytrain.apps.operators.models import OperatingCompany

from refundmytrain.libs.rail_fields import (
    StanoxField, TrainMovementEventField, TrainIDField
)

from .train_entity import TrainEntity
from .message_id_mixin import MessageIDMixin
from .train_id_mixin import TrainIDMixin


class TrainActivationMessage(MessageIDMixin, TrainIDMixin, models.Model):
    """
    Message type 1
    http://nrodwiki.rockshore.net/index.php/Train_Activation
    """

    train_entity = models.ForeignKey(TrainEntity)

    train_schedule_uid = models.CharField(
        max_length=10,
        unique=False,
        db_index=True,
    )
    # train_schedule = models.ForeignKey(TrainSchedule)

    schedule_start_date = models.DateField()

    schedule_end_date = models.DateField()

    schedule_source = models.CharField(
        max_length=1,
        help_text=(
            'Set to C for schedules from CIF/ITPS, or V for schedules from'
            ' VSTP/TOPS'
        )
    )

    schedule_type = models.CharField(
        max_length=1,
        help_text=(
            'Either C (Cancellation), N (New STP), O (STP Overlay) or '
            'P (Permanent i.e. as per the WTT/LTP)'
        )
    )
