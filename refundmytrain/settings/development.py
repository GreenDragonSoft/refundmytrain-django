from .common import *

import logging
import os

LOG = logging.getLogger(__name__)

DEBUG = True


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
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'log', 'debug.log'),
            'formatter': 'verbose',
        },
        'info_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'log', 'info.log'),
            'formatter': 'verbose',
        },
        'warning_file': {
            'level': 'WARN',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'log', 'warning.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['debug_file', 'info_file', 'warning_file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# TOTALLY INSECURE: We use a single secret in development, not in production :)
SECRET_KEY = "xanXgBP3nKIoGI6aMxGz14oApj1YZZzW4iZzSp5Gc+m+Nh1qIu8pZeKWRRK0"
INTERNAL_IPS = ['127.0.0.1', '::1', '10.0.2.2']

INSTALLED_APPS += [
    'debug_toolbar',
]


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
