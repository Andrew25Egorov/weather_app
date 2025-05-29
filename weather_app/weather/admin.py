from django.contrib import admin
from .models import CitySearch


@admin.register(CitySearch)
class CitySearchAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'country', 'search_count', 'last_search')
    search_fields = ('city_name', 'country')
    list_filter = ('last_search',)
    ordering = ('-search_count',)
