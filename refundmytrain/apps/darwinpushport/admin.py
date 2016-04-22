from django.contrib import admin

from refundmytrain.apps.darwinpushport.models import (
    CancellationReason, CallingPoint, OperatingCompany, LateRunningReason,
    Location, TimetableJourney, ImportLog, JourneyFromTo
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
        'calling_point_type',
        'location',
        'timetable_arrival_time',
        'timetable_arrival_datetime',
        'timetable_departure_time',
        'timetable_departure_datetime',

        # unbound callable, see http://stackoverflow.com/a/5684745
        CallingPoint.actual_arrival_time,
    )

    readonly_fields = fields


class MinutesLateFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'minutes late'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'timetable_variation'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('15+', '> 15 min'),
            ('30+', '> 30 min'),
            ('60+', '> 1hr'),
            ('120+', '> 2hr'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if self.value() == '15+':
            return queryset.filter(
                maximum_minutes_late__gte=15)

        elif self.value() == '30+':
            return queryset.filter(
                maximum_minutes_late__gte=30)

        elif self.value() == '60+':
            return queryset.filter(
                maximum_minutes_late__gte=60)

        elif self.value() == '120+':
            return queryset.filter(
                maximum_minutes_late__gte=120)


@admin.register(TimetableJourney)
class TimetableJourneyAdmin(admin.ModelAdmin):
    list_display = (
        'rtti_train_id',
        'start_date',
        'start',
        'end',
        'operating_company',
        'maximum_minutes_late',
        'num_calling_points',
        'train_uid',
        'train_id',
        'late_reason',
    )

    search_fields = (
        'rtti_train_id',
        'operating_company__name',
    )

    inlines = [CallingPointInline]

    list_filter = (
        'start_date',
        MinutesLateFilter,
        'late_reason',
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


@admin.register(CancellationReason)
@admin.register(LateRunningReason)
class ReasonAdmin(admin.ModelAdmin):
    list_display = ('code', 'text')
    search_fields = list_display
