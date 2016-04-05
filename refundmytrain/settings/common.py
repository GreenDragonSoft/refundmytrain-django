"""
Django settings for refundmytrain project on Heroku. Fore more info, see:
https://github.com/heroku/heroku-django-template

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import sys

from os.path import abspath, dirname, join as pjoin
from django.core.exceptions import ImproperlyConfigured

# BASE_DIR should be the directory where `manage.py` is located. In our case
# it's the top of the git repo.
BASE_DIR = abspath(pjoin(dirname(__file__), '..', '..'))

PROJECT_ROOT = abspath(pjoin(dirname(__file__), '..'))

sys.path.append(pjoin(PROJECT_ROOT, 'apps'))
sys.path.append(pjoin(PROJECT_ROOT, 'libs'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django_nose',
    'storages',
    'rest_framework',

    'refundmytrain.apps.corpus',
    'refundmytrain.apps.naptan',
    'refundmytrain.apps.corpus_naptan_link',
    'refundmytrain.apps.operators',
    'refundmytrain.apps.trainmovements',
    'refundmytrain.apps.darwinpushport',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

ROOT_URLCONF = 'refundmytrain.urls'

TEMPLATES = (
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,  # TODO: reconfigure this in dev settings file
        },
    },
)

WSGI_APPLICATION = 'refundmytrain.wsgi.application'


AUTH_PASSWORD_VALIDATORS = (
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
)

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True

TIME_FORMAT = 'H:i'
DATE_FORMAT = 'l jS N'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


if os.environ.get('USE_FILESYSTEM_STORAGE', 'false') == 'true':
    MEDIA_ROOT = abspath(pjoin(BASE_DIR, 'uploads'))
    MEDIA_URL = '/media-uploads/'

    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

    FILESYSTEM_BASED_MEDIA = True  # Used in urls.py

else:
    try:
        AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
        AWS_S3_ACCESS_KEY_ID = os.environ['AWS_S3_ACCESS_KEY_ID']
        AWS_S3_SECRET_ACCESS_KEY = os.environ['AWS_S3_SECRET_ACCESS_KEY']
    except KeyError:
        raise ImproperlyConfigured(
            'In production mode, Django reads environment variables '
            'specifying the S3 bucket & credentials used for media uploads. '
            'Required keys are: AWS_STORAGE_BUCKET_NAME, '
            'AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY. In development, '
            'you can use local storage: `export USE_FILESYSTEM_STORAGE=true`')

    STATICFILES_LOCATION = 'static'
    STATICFILES_STORAGE = 'refundmytrain.custom_storages.StaticStorage'

    MEDIAFILES_LOCATION = 'uploads'
    DEFAULT_FILE_STORAGE = 'refundmytrain.custom_storages.MediaStorage'

    FILESYSTEM_BASED_MEDIA = False  # Used in urls.py
