from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('weather/', views.get_weather, name='get_weather'),
    path('autocomplete/',
         csrf_exempt(views.autocomplete),
         name='autocomplete'),
    # path('api/search-history/',
    #      csrf_exempt(views.search_history_api),
    #      name='search_history_api'),
]
