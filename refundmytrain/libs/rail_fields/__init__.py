from django.db import models
from django.core.validators import RegexValidator


class StanoxField(models.CharField):
    # https://docs.djangoproject.com/en/1.9/howto/custom-model-fields/#writing-a-field-subclass

    PATTERN = r'\d{5}\*?'

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 6
        kwargs['validators'] = [RegexValidator(self.PATTERN)]

        super(StanoxField, self).__init__(*args, **kwargs)


class TrainMovementEventField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 11
        kwargs['choices'] = (
            ("ARRIVAL", 'Arrival'),
            ("DEPARTURE", 'Departure'),
            ("DESTINATION", 'Destination'),
        )

        super(TrainMovementEventField, self).__init__(*args, **kwargs)
