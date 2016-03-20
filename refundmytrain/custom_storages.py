from django.conf import settings
from storages.backends.s3boto import S3BotoStorage

# TODO: ultimately, put these into separate S3 buckets using the `bucket_name`
# class field


class StaticStorage(S3BotoStorage):
    location = settings.STATICFILES_LOCATION
    # Don't use AWS signed URLS, these files are public
    querystring_auth = False


class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION
    querystring_auth = True
