from django.db import models

from refundmytrain.libs.rail_fields import TrainIDField


class TrainIDMixin(models.Model):
    class Meta:
        abstract = True

    train_id = TrainIDField()
