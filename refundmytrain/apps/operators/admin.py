from django.contrib import admin

from refundmytrain.apps.operators.models import OperatingCompany


@admin.register(OperatingCompany)
class OperatingCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'atoc_code', 'numeric_code')
    search_fields = list_display
    readonly_fields = list_display
