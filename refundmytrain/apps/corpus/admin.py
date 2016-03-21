from django.contrib import admin

from refundmytrain.apps.corpus.models import CorpusLocation


@admin.register(CorpusLocation)
class CorpusLocationAdmin(admin.ModelAdmin):
    list_display = ('three_alpha', 'tiploc', 'uic_code', 'stanox',
                    'national_location_code', 'nlc_description',
                    'nlc_short_description')
    search_fields = list_display
    readonly_fields = list_display
