from django.db import models

# from refundmytrain.apps.naptan.models import NaptanRailStation
# from refundmytrain.apps.operators.models import OperatingCompany

from refundmytrain.libs.rail_fields import (
    StanoxField, TrainMovementEventField, TrainIDField
)

from .message_id_mixin import MessageIDMixin
from .train_id_mixin import TrainIDMixin


class TrainReinstatementMessage(MessageIDMixin, TrainIDMixin, models.Model):
    """
    Message type 5
    http://nrodwiki.rockshore.net/index.php/Train_Reinstatement
    """
    pass
