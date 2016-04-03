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

LOG_DIR = '/var/log/refundmytrain'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'debug.log'),
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'info_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'info.log'),
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'warning_file': {
            'level': 'WARN',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'warning.log'),
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['debug_file', 'info_file', 'warning_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
