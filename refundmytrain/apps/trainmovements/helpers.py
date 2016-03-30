from refundmytrain.apps.operators.helpers import (
    operating_company_by_numeric_code)

from .models import (
    TrainEntity, TrainActivationMessage, TrainMovementMessage,
    TrainCancellationMessage, TrainReinstatementMessage
)

from .parsers import TrainMovementParser


def bulk_ingest_messages(messages):
    for msg in messages:
        ingest_message(msg['message_id'], msg)

    # TODO: actually use bulk create!


def ingest_message(url_message_id, message):

    data_message_id, header, body = (
        message['message_id'],
        message['header'],
        message['body']
    )

    assert url_message_id == data_message_id

    train_entity, _ = TrainEntity.objects.get_or_create(
        train_id=body['train_id']
    )

    create_func = MSG_TYPES.get(int(header['msg_type']))

    if create_func is not None:
        create_func(url_message_id, body, train_entity)


def make_train_movement_message(message_id, body, train_entity):
    # "body": {
    #     "loc_stanox": "45150",
    #     "train_file_address": null,
    #     "division_code": "55",
    #     "train_id": "541H08MY20",
    #     "direction_ind": "DOWN",
    #     "event_source": "AUTOMATIC",
    #     "line_ind": "M",
    #     "original_loc_timestamp": "",
    #     "next_report_stanox": "45106",
    #     "delay_monitoring_point": "true",
    #     "train_service_code": "21750001",
    #     "planned_timestamp": "1458505710000",
    #     "variation_status": "LATE",
    #     "current_train_id": "",
    #     "event_type": "DEPARTURE",
    #     "next_report_run_time": "6",
    #     "offroute_ind": "false",
    #     "auto_expected": "true",
    #     "train_terminated": "false",
    #     "gbtt_timestamp": "",
    #     "route": "1",
    #     "original_loc_stanox": "",
    #     "toc_id": "55",
    #     "correction_ind": "false",
    #     "platform": "",
    #     "actual_timestamp": "1458505980000",
    #     "planned_event_type": "DEPARTURE",
    #     "timetable_variation": "5",
    #     "reporting_stanox": "45150"
    # }

    obj, created = TrainMovementMessage.objects.update_or_create(
        message_id=message_id,
        defaults=TrainMovementParser(body).parse()
    )


MSG_TYPES = {
    3: make_train_movement_message,
}
