import logging

from refundmytrain.apps.operators.helpers import (
    operating_company_by_numeric_code)

from .models import (
    TrainEntity,
    # TrainActivationMessage,
    TrainMovementMessage,
    # TrainCancellationMessage,
    # TrainReinstatementMessage
)

from .parsers import TrainMovementParser

LOG = logging.getLogger(__name__)


def bulk_ingest_messages(messages):
    for msg in messages:
        ingest_message(msg['message_id'], msg)

    # TODO: actually use bulk create!


def ingest_message(url_message_id, message):

    data_message_id, msg_type, body = (
        message['message_id'],
        int(message['header']['msg_type']),
        message['body']
    )

    assert url_message_id == data_message_id

    try:
        model_class, parser_class = MSG_TYPES[msg_type]
    except KeyError:
        LOG.warning("Don't know how to handle msg type {}".format(msg_type))
    else:
        create_message(url_message_id, body, model_class, parser_class)


def create_message(message_id, body, model_class, parser_class):
    obj, created = model_class.objects.update_or_create(
        message_id=message_id,
        defaults=parser_class(body).parse()
    )
    return obj, created


MSG_TYPES = {
    3: (TrainMovementMessage, TrainMovementParser),
}
