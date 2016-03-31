from django.db import models

from refundmytrain.libs.rail_fields import TrainIDField


class TrainEntity(models.Model):
    """
    The train entity refers to a single run of a train on a specific day
    whereas the schedule entity is potentially valid for several months at a
    time.
    """

    train_id = TrainIDField(primary_key=True)

    def __str__(self):
        return '<TrainEntity {}>'.format(self.train_id)

    def has_activation(self):
        return self.activation_message is not None

    @property
    def number_of_messages(self):
        return self.messages.count()

    @property
    def activation_message(self):
        return None  # TODO

    # TODO: make a property creation_datetime that looks it up in the
    # activatin message, if any
    # creation_datetime = models.DateTimeField(
    #     help_text=(
    #         'The timestamp when the train was originally created in TRUST.'
    #     )
    # )
