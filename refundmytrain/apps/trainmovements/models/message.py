from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


from .train_entity import TrainEntity


class Message(models.Model):
    content_type = models.ForeignKey(ContentType)
    message_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'message_id')

    train_entity = models.ForeignKey(
        TrainEntity,
        related_name='messages'
    )
