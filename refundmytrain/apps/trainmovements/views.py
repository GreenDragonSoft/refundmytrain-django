import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException

# from .serializers import TrainMovementMessageSerializer
from .helpers import ingest_message, bulk_ingest_messages

LOG = logging.getLogger(__name__)


class TrainMovementsMessageCreateOrUpdate(APIView):
    """
    Insert a message, overwriting it if necessary based on the message_id
    in the URL.
    """

    def put(self, request, *args, **kwargs):
        given_message_id = self.kwargs['pk']  # Get message UUID from URL

        ingest_message(given_message_id, request.data)
        return Response({'message': 'OK'})


class TrainMovementsMessageCreate(APIView):
    """
    Bulk insert multiple messages without checking whether they've been
    previously inserted.

    Atomic: all or zero messages will be inserted.
    """

    def post(self, request, *args, **kwargs):
        messages = request.data

        if not isinstance(messages, list):
            messages = [messages]

        try:
            bulk_ingest_messages(messages)
        except Exception as e:
            LOG.exception(e)
            raise APIException({'message': str(e)})

        return Response({'message': 'OK'})
