from django.contrib import admin

from refundmytrain.apps.darwinpushport.models import (
    OperatingCompany, Location)


@admin.register(OperatingCompany)
class OperatingCompanyAdmin(admin.ModelAdmin):
    list_display = ('atoc_code', 'name')
    search_fields = list_display

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('tiploc', 'three_alpha', 'name')
    search_fields = list_display

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]
