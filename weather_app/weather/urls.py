from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('weather/', views.get_weather, name='get_weather'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('api/stats/', views.city_stats_api, name='city_stats_api'),
]
