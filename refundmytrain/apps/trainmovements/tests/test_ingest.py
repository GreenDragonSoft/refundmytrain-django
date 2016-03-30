import gzip
import json
import os

from refundmytrain.apps.trainmovements.helpers import ingest_message


SAMPLE_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', '..', 'data')


def test_ingest_sample_messages():
    for filename in os.listdir(os.path.join(SAMPLE_DIR)):
        if filename.endswith('.json.gz'):
            yield _ingest_file, os.path.join(SAMPLE_DIR, filename)


def _ingest_file(filename):
    with gzip.open(filename, 'rb') as f:
        message = json.loads(f.read().decode('utf-8'))

        ingest_message(
            message['message_id'],
            message
        )
