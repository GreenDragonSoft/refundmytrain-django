from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save

from .message import Message
from .train_entity import TrainEntity

from .train_activation_message import TrainActivationMessage
from .train_movement_message import TrainMovementMessage
from .train_cancellation_message import TrainCancellationMessage
from .train_reinstatement_message import TrainReinstatementMessage


def attach_message_object(sender, instance, created, **kwargs):
    if created:
        ctype = ContentType.objects.get_for_model(instance)

        train_entity, _ = TrainEntity.objects.get_or_create(
            train_id=instance.train_id)

        Message.objects.get_or_create(
            content_type=ctype,
            message_id=instance.message_id,
            train_entity=train_entity)

post_save.connect(attach_message_object, sender=TrainActivationMessage)
post_save.connect(attach_message_object, sender=TrainMovementMessage)
post_save.connect(attach_message_object, sender=TrainCancellationMessage)
post_save.connect(attach_message_object, sender=TrainReinstatementMessage)
