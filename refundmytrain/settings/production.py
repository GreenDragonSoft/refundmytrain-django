from .common import *

from django.core.exceptions import ImproperlyConfigured

import dj_database_url

try:
    SECRET_KEY = os.environ['SECRET_KEY']
except KeyError:
    raise ImproperlyConfigured(
        "In production mode you must specify the `SECRET_KEY` environment "
        "variable. If you're _definitely not_ running in production it's safe "
        "to set this to something insecure, eg `export SECRET_KEY=foo`")

# Set database config from $DATABASE_URL.
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES = {'default': db_from_env}

ALLOWED_HOSTS = [
    '*'  # FIXME: Don't run a real service like this!
]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
