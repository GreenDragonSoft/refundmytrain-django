from django.db import models

from refundmytrain.apps.naptan.models import NaptanRailStation
from refundmytrain.apps.operators.models import OperatingCompany

from refundmytrain.libs.rail_fields import (
    StanoxField, TrainMovementEventField, TrainIDField
)

from .train_entity import TrainEntity


class TrainMovementMessage(models.Model):
    """
    Message type: 3
    http://nrodwiki.rockshore.net/index.php/Train_Movement
    """

    message_id = models.UUIDField(
        primary_key=True,
        help_text='Our own identifier: not part of TRUST or the rail system')

    train_id = TrainIDField()

    train_entity = models.ForeignKey(
        TrainEntity,
        related_name='train_movement_messages'
    )

    actual_datetime = models.DateTimeField(
        help_text=(
            'The date and time that this event happened at the location'
        )
    )

    location_stanox = StanoxField(
        help_text=(
            'The STANOX of the location at which this event happened'
        )
    )

    location_station = models.ForeignKey(
        NaptanRailStation,
        null=True,
    )

    timetable_datetime = models.DateTimeField(
        null=True,
        help_text=(
            'The planned GBTT (passenger) date and time that the event was '
            'due to happen at this location'
        )
    )

    planned_datetime = models.DateTimeField(
        null=True,
        help_text=(
            'The planned date and time that this event was due to happen at '
            'this location'
        )
    )

    original_location_stanox = StanoxField(
        null=True,
        help_text=(
            'If the location has been revised, the STANOX of the location '
            'in the schedule at activation time'
        )
    )

    original_location_station = models.ForeignKey(
        NaptanRailStation,
        null=True,
        related_name='changed_train_movement_messages',
    )

    original_location_datetime = models.DateTimeField(
        null=True,
        help_text=(
            'The planned departure time associated with the original location'
        )
    )

    planned_event_type = TrainMovementEventField(
        help_text=(
            'The planned type of event - one of "ARRIVAL", "DEPARTURE" or '
            '"DESTINATION"'
        )
    )

    event_type = TrainMovementEventField(
        help_text=(
            'The type of event - either "ARRIVAL" or "DEPARTURE"'
        )
    )

    event_source = models.CharField(
        max_length=10,
        help_text=(
            'Whether the event source was "AUTOMATIC" from SMART, or '
            '"MANUAL" from TOPS or TRUST SDR'
        )
    )

    is_correction = models.BooleanField(
        help_text=(
            'Whether this report is a correction of a previous report'
        )
    )

    is_off_route = models.BooleanField(
        # Always present
        help_text=(
            'Whether this report is for a location OFF schedule'
        )
    )

    direction = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        help_text=(
            'For automatic reports, either "UP" or "DOWN" depending on the '
            'direction of travel'
        )
    )

    line_indicator = models.CharField(
        null=True,
        blank=True,
        max_length=1,
        help_text=(
            'A single character (or blank) depending on the line the train '
            'is travelling on, e.g. F = Fast, S = Slow'
        ),
        choices=(('F', 'Fast'), ('S', 'Slow')),
    )

    platform = models.CharField(
        null=True,
        blank=True,
        max_length=3,
        help_text=(
            'Two characters (including a space for a single character) or '
            'blank if the movement report is associated with a platform number'
        )
    )

    route = models.CharField(
        null=True,
        blank=True,
        max_length=1,
        help_text=(
            'A single character (or blank) to indicate the exit route '
            'from this location'
        )
    )

    current_train_entity = models.ForeignKey(
        TrainEntity,
        null=True,
        help_text=(
            'Where a train has had its identity changed, the current '
            '10-character unique identity for this train'
        ),
        related_name='changed_identity_train_movement_messages',
    )

    train_service_code = models.CharField(
        max_length=16,  # TODO
        help_text=(
            'Train service code as per schedule'
        )
    )

    operating_company = models.ForeignKey(
        OperatingCompany,
        null=True,
        help_text=(
            'Operating company ID as per TOC Codes'
        )
    )

    # division_code = models.ForeignKey(OperatingCompany)
    #     help_text=(
    #         'Operating company ID as per TOC Codes'
    #     )
    # )

    timetable_variation = models.PositiveSmallIntegerField(
        null=True,
        help_text=(
            'The number of minutes variation from the scheduled time at '
            'this location. Off-route reports will contain "0"'
        )
    )

    variation_status = models.CharField(
        max_length=10,
        choices=(
            ('ON TIME', 'On time'),
            ('EARLY', 'Early'),
            ('LATE', 'Late'),
            ('OFF ROUTE', 'Off route'),
        ),
        help_text=(
            'One of "ON TIME", "EARLY", "LATE" or "OFF ROUTE"'
        ),
    )

    next_report_stanox = StanoxField(
        null=True,
        help_text=(
            'The STANOX of the location at which the next report for this '
            'train is due.'
        )
    )

    next_report_station = models.ForeignKey(
        NaptanRailStation,
        null=True,
        related_name='next_report_train_movement_messages'
    )

    next_report_run_time = models.PositiveSmallIntegerField(
        null=True,
        help_text=(
            'The running time to the next location in minutes.'
        )
    )

    is_train_terminated = models.BooleanField(
        help_text=(
            'Whether the train has completed its journey.'
        )
    )

    is_delay_monitoring_point = models.BooleanField(
        help_text=(
            'Whether this is a delay monitoring point. Off-route reports '
            'will contain "false"'
        )
    )

    train_file_address = models.CharField(
        null=True,
        blank=True,
        max_length=16,  # TODO
        help_text=(
            'The TOPS train file address, if applicable'
        )
    )

    reporting_stanox = StanoxField(
        null=True,
        help_text=(
            'The STANOX of the location that generated this report. Set '
            'to "00000" for manual and off-route reports'
        )
    )

    reporting_station = models.ForeignKey(
        NaptanRailStation,
        null=True,
        related_name='reporting_station_train_movement_messages',
    )

    is_auto_expected = models.NullBooleanField(
        help_text=(
            'Whether an automatic report is expected for this location.'
        )
    )
