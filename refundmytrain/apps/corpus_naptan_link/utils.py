from refundmytrain.apps.corpus.models import CorpusLocation
from .models import CorpusNaptanLink


def get_naptan_rail_station(stanox):
    """
    Return exactly one NaptanRailStation for the given STANOX code.
    """

    for link in CorpusNaptanLink.objects.filter(
            corpus_location__stanox=stanox):
        return link.naptan_rail_station  # Return the first, if matching

    # Not found, try and explain why.

    corpus_locations = CorpusLocation.objects.filter(stanox=stanox)

    if corpus_locations.count() == 0:
        raise ValueError('Failed to find STANOX `{}` in the Network Rail '
                         'CORPUS data :S'.format(stanox))

    elif corpus_locations.count() >= 1:
        raise ValueError("STANOX `{}` didn't match a public (NATPAN) rail "
                         "station, although it matched these entries in the "
                         "network rail CORPUS data: {}".format(
                             stanox,
                             ', '.join([str(x) for x in corpus_locations])))
