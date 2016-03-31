from django.contrib import admin

from refundmytrain.apps.trainmovements.models import (
    TrainEntity, TrainMovementMessage)


@admin.register(TrainEntity)
class TrainEntityAdmin(admin.ModelAdmin):
    list_display = ('train_id', 'has_activation', 'number_of_messages')
    search_fields = ('train_id',)

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


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
                variation_status='LATE',
                timetable_variation__gte=15)

        elif self.value() == '30+':
            return queryset.filter(
                variation_status='LATE',
                timetable_variation__gte=30)

        elif self.value() == '60+':
            return queryset.filter(
                variation_status='LATE',
                timetable_variation__gte=60)

        elif self.value() == '120+':
            return queryset.filter(
                variation_status='LATE',
                timetable_variation__gte=120)


@admin.register(TrainMovementMessage)
class TrainMovementMessageAdmin(admin.ModelAdmin):
    list_display = (
        'message_id',
        'train_id',
        'location_station',
        'operating_company',
        'variation_status',
        'timetable_variation',
    )

    list_filter = (
        'variation_status',
        MinutesLateFilter,
        'operating_company',
    )

    search_fields = (
        '=train_entity__train_id',
        'location_station__name',
        '=location_station__three_alpha',
        '=location_stanox',
        '=reporting_stanox',
    )

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]
