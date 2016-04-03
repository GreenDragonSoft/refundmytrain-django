from django.contrib import admin

from refundmytrain.apps.darwinpushport.models import (
    CallingPoint, OperatingCompany, Location, TimetableJourney,
    ImportLog)


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


class CallingPointInline(admin.TabularInline):
    model = CallingPoint
    extra = 0
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


@admin.register(TimetableJourney)
class TimetableJourneyAdmin(admin.ModelAdmin):
    list_display = (
        'rtti_train_id',
        'start_date',
        'start',
        'end',
        'operating_company',
        'num_calling_points',
        'train_uid',
        'train_id',
    )

    search_fields = (
        'rtti_train_id',
        'operating_company__name',
    )

    inlines = [CallingPointInline]

    list_filter = (
        'start_date',
    )

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ('filename', 'import_datetime')
    search_fields = ('filename',)
