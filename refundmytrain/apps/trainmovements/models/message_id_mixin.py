from django.db import models


class MessageIDMixin(object):
    message_id = models.UUIDField(
        primary_key=True,
        help_text='Our own identifier: not part of TRUST or the rail system')
