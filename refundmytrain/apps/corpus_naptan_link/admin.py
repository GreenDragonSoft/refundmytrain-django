from django.contrib import admin

from refundmytrain.apps.corpus_naptan_link.models import CorpusNaptanLink


@admin.register(CorpusNaptanLink)
class CorpusNaptanLinkAdmin(admin.ModelAdmin):
    list_display = ('corpus_location', 'naptan_rail_station', 'flag_warning')
    search_fields = list_display
    readonly_fields = list_display
