from django.contrib import admin

from refundmytrain.apps.naptan.models import NaptanRailStation


@admin.register(NaptanRailStation)
class NaptanRailStationAdmin(admin.ModelAdmin):
    list_display = ('three_alpha', 'tiploc', 'name')
    search_fields = list_display
    readonly_fields = list_display
