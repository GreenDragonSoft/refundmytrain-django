class TrainMovementParser(object):
    def __init__(self, message_body):
        self.body = message_body

    def parse(self):
        return {

            'train_entity': train_entity,

            'train_id': self.body['train_id'],

            'location_stanox': self.body['loc_stanox'],              # eg "45150"

            'location_station': null_or(
                stanox_to_station, self.body['loc_stanox']),

            'train_file_address': self.body['train_file_address'],   # eg IC2, null

            # foo=decode(self.body['division_code']),  # eg "55",
            'direction': self.body['direction_ind'],            # eg "DOWN",

            'event_source': self.body['event_source'],          # eg "AUTOMATIC",

            'line_indicator': self.body['line_ind'],            # eg "M",

            'original_location_datetime': null_or(
                decode_timestamp, self.body['original_loc_timestamp']),

            'next_report_stanox': self.body['next_report_stanox'],  # eg "45106"

            'next_report_station': null_or(
                stanox_to_station, self.body['next_report_stanox']),   # eg "45106"

            'train_service_code': self.body['train_service_code'],   # eg "21750001"

            'variation_status': self.body['variation_status'],       # eg "LATE",

            # current_train_entity=self.body['current_train_id'],    # eg "",  TODO

            'event_type': self.body['event_type'],  # eg "DEPARTURE",

            'next_report_run_time': null_or(
                int, self.body['next_report_run_time']),  # eg "6",

            'is_delay_monitoring_point': decode_bool(
                self.body['delay_monitoring_point']),

            'is_off_route': decode_bool(
                self.body['offroute_ind']),

            'is_auto_expected': null_or(
                decode_bool, self.body['auto_expected']),

            'is_train_terminated': decode_bool(
                self.body['train_terminated']),

            'is_correction': decode_bool(
                self.body['correction_ind']),

            'planned_datetime': null_or(
                decode_timestamp, self.body['planned_timestamp']),

            'timetable_datetime': null_or(
                decode_timestamp, self.body['gbtt_timestamp']),

            'route': self.body['route'],                              # eg "1",

            'original_location_stanox': null_or(
                str, self.body['original_loc_stanox']),  # eg "",

            'original_location_station': null_or(
                stanox_to_station, self.body['original_loc_stanox']),

            'operating_company': null_or(
                    operating_company_by_numeric_code, self.body['toc_id']),

            'platform': null_or(
                str, self.body['platform']),

            'actual_datetime': null_or(                  # eg "1458505980000"
                decode_timestamp, self.body['actual_timestamp']),

            'planned_event_type': self.body['planned_event_type'],  # eg "DEPARTURE"

            'timetable_variation': null_or(
                int, self.body['timetable_variation']),  # eg "5",

            'reporting_stanox': null_or(
                str, self.body['reporting_stanox']),    # eg "45150"

            'reporting_station': null_or(
                stanox_to_station, self.body['reporting_stanox']),
        }
