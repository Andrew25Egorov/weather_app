from django.contrib import admin

from .models import CitySearch


@admin.register(CitySearch)
class CitySearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'count', 'last_searched')
    search_fields = ('name',)
    ordering = ('-count',)
