from django.contrib import admin

from refundmytrain.apps.darwinpushport.models import (
    CallingPoint, OperatingCompany, Location, TimetableJourney,
    ImportLog, JourneyFromTo
)


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

    fields = (
        'location',
        'timetable_arrival_time',
        'timetable_arrival_datetime',
        'timetable_departure_time',
        'timetable_departure_datetime',

        # unbound callable, see http://stackoverflow.com/a/5684745
        CallingPoint.get_actual_arrival,
    )

    readonly_fields = fields


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


@admin.register(JourneyFromTo)
class JourneyFromToAdmin(admin.ModelAdmin):
    list_display = ('from_location', 'to_location', 'num_journeys')
    search_fields = (
        'from_location__three_alpha',
        'to_location__three_alpha',
    )


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ('filename', 'import_datetime')
    search_fields = ('filename',)
