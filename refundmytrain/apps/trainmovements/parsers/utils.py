import datetime
import pytz

from refundmytrain.apps.corpus_naptan_link.utils import get_naptan_rail_station

UK_TIMEZONE = pytz.timezone('Europe/London')


def null_or(decode_func, value):
    if value is None or value == '':
        return None

    return decode_func(value)


def decode_bool(string):
    return {
        'true': True,
        'false': False,
    }[string.lower()]


def decode_timestamp(string):
    """
    Timestamp appears to be in milliseconds:
    `1455887700000` : Tue, 31 Mar in the year 48105.
    `1455887700`    : Fri, 19 Feb 2016 13:15:00 GMT
    """

    try:
        return UK_TIMEZONE.localize(
            datetime.datetime.fromtimestamp(int(string) / 1000)
        )
    except ValueError as e:
        raise ValueError('Choked on `{}`: {}'.format(string, repr(e)))


def stanox_to_station(stanox):
    if stanox.strip() == '00000':
        return None

    try:
        return get_naptan_rail_station(stanox)
    except ValueError as e:
        print(repr(e))
        return None
