import contextlib
import gzip
import os
import re
import sys

from ftplib import FTP

import atomicfile

from django.conf import settings
from django.core.management.base import BaseCommand

from refundmytrain.apps.darwinpushport.models import (
    ImportLog
)

from refundmytrain.apps.darwinpushport.importers import (
    import_reference_data, import_schedule, import_push_port_messages
)

PUSH_PORT_PATTERN = 'pPortData.log.\d{4}-\d{2}-\d{2}-\d{2}-\d{2}'
REFERENCE_PATTERN = '\d+_ref_v3.xml.gz'
SCHEDULE_PATTERN = '\d+_v8.xml.gz'

DATA_DIR = os.path.join(settings.PROJECT_ROOT, '..', '..', 'darwin_data')


def print_func(text, *args, **kwargs):
    sys.stdout.write(text + '\n', *args, **kwargs)

PRINT = print_func


class Command(BaseCommand):
    help = ('Updates the DARWIN reference data, timetable and gets latest '
            'push port data. Records latest version received in the db.')

    def handle(self, *args, **options):
        global PRINT
        PRINT = self.stdout.write

        host = os.environ['DARWIN_DATA_FEEDS_HOST']
        username = os.environ['DARWIN_DATA_FEEDS_USERNAME']
        password = os.environ['DARWIN_DATA_FEEDS_PASSWORD']

        handle(host, username, password)
        self.stdout.write(self.style.SUCCESS('OK'))


def handle(host, username, password):
    with FTP(host) as ftp:
        ftp.login(username, password)

        download_latest(ftp)


def download_latest(ftp):
    (
        reference_files,
        schedule_files,
        push_port_files,
        unknown_files
    ) = categorise_filenames(get_file_listing(ftp))

    for filename in reference_files:
        if not already_loaded(filename):
            with download_file(ftp, filename) as fobj:
                load_reference_file(filename, fobj)
                record_loaded(filename)

    for filename in schedule_files:
        if not already_loaded(filename):
            with download_file(ftp, filename) as fobj:
                load_schedule_file(filename, fobj)
                record_loaded(filename)
                pass

    for filename in push_port_files:
        if not already_loaded(filename):
            with download_file(ftp, filename) as fobj:
                load_push_port_file(filename, fobj)
                record_loaded(filename)


def already_loaded(filename):
    if ImportLog.objects.filter(
            filename=normalize_filename(filename)).count() > 0:
        PRINT('Already loaded: {}'.format(filename))
        return True

    return False


def record_loaded(filename):
    ImportLog.objects.create(filename=normalize_filename(filename))


def normalize_filename(filename):
    return re.sub('.gz$', '', filename)


def categorise_filenames(filenames):
    reference_files = []
    schedule_files = []
    push_port_files = []
    unknown_files = []

    while True:
        try:
            filename = filenames.pop(0)
        except IndexError:
            break

        if re.match(REFERENCE_PATTERN, filename):
            reference_files.append(filename)

        elif re.match(SCHEDULE_PATTERN, filename):
            schedule_files.append(filename)

        elif re.match(PUSH_PORT_PATTERN, filename):
            push_port_files.append(filename)

        else:
            unknown_files.append(filename)

    PRINT('{} reference files'.format(len(reference_files)))
    PRINT('{} schedule files'.format(len(schedule_files)))
    PRINT('{} push port files'.format(len(push_port_files)))
    PRINT('unknown files: {}'.format(unknown_files))
    return reference_files, schedule_files, push_port_files, unknown_files


def get_file_listing(ftp):
    filenames = []

    def line_callback(line):
        filenames.append(line.split()[-1])

    ftp.dir(line_callback)
    return filenames


@contextlib.contextmanager
def download_file(ftp, filename):
    """
    Download the given filename from the FTP server, saving it to a temporary
    file. Return a context manager with the open file (read mode) and
    delete it on exit.
    """

    download_filename = os.path.join(DATA_DIR, filename)

    if not os.path.isfile(download_filename):
        with atomicfile.AtomicFile(download_filename, 'wb') as f:
            PRINT('Downloading {}...'.format(filename))
            ftp.retrbinary('RETR {}'.format(filename), f.write)

    with open(download_filename, 'rb') as f:
        yield f


def load_push_port_file(filename, f):
    PRINT('Loading push port data {}'.format(filename))
    import_push_port_messages(f)


def load_reference_file(filename, f):
    PRINT('Loading reference data {}'.format(filename))
    with gzip.GzipFile(fileobj=f, mode='rb') as f_unzipped:
        locations, operating_companies = import_reference_data(f_unzipped)

        PRINT('Loaded {} locations, {} operating_companies'.format(
            locations, operating_companies))


def load_schedule_file(filename, f):
    PRINT('Loading schedule file {}'.format(filename))
    with gzip.GzipFile(fileobj=f, mode='rb') as f_unzipped:
        num_journeys = import_schedule(f_unzipped)

        PRINT('Loaded {} journeys'.format(num_journeys))
