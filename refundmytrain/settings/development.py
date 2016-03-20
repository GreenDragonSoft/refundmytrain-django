from .common import *

import logging
import os

LOG = logging.getLogger(__name__)

DEBUG = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'log', 'debug.log'),
        },
        'info_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'log', 'info.log'),
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['debug_file', 'info_file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# TOTALLY INSECURE: We use a single secret in development, not in production :)
SECRET_KEY = "xanXgBP3nKIoGI6aMxGz14oApj1YZZzW4iZzSp5Gc+m+Nh1qIu8pZeKWRRK0"


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    # Use a local postgres socket a-la the psql command. Assumes you have a
    # postgres user AND database both called `vagrant`.
    # http://stackoverflow.com/a/23871618
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'vagrant',
    }
}

# Allow all host headers
ALLOWED_HOSTS = ['*']
