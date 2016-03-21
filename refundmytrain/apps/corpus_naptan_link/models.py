from django.db import models
from refundmytrain.apps.naptan.models import NaptanRailStation
from refundmytrain.apps.corpus.models import CorpusLocation


class CorpusNaptanLink(models.Model):

    def __str__(self):
        return 'CorpusNaptanLink(corpus="{}", station="{}">'.format(
            self.corpus_location, self.naptan_rail_station)

    # stanox = models.CharField(
    #     unique=True,  # We need an unambiguous search from STANOX
    #     max_length=10,
    #     help_text=('Station Number - these codes can refer to non-station '
    #                'locations such as sidings and junctions. STANOX codes '
    #                'are grouped by geographical area - the first two digits '
    #                'specify the area in which the location exists.')
    # )

    corpus_location = models.OneToOneField(CorpusLocation)
    naptan_rail_station = models.OneToOneField(NaptanRailStation)
    flag_warning = models.CharField(max_length=100, null=True, blank=True)
