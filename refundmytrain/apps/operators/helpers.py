import logging

from .models import OperatingCompany

LOG = logging.getLogger(__name__)


def operating_company_by_numeric_code(numeric_code):
    try:
        return OperatingCompany.objects.get(
            numeric_code=numeric_code
        )

    except OperatingCompany.DoesNotExist:
        LOG.warning('Failed to lookup operating company for code `{}`'.format(
            numeric_code))
        return None

    except OperatingCompany.MultipleObjectsReturned:
        LOG.warning('Multiple operators for code `{}`, picking 1st'.format(
            numeric_code))
        return OperatingCompany.objects.filter(
            numeric_code=numeric_code)[0]
