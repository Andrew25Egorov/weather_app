from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    # Главная страница с формой поиска
    path('', views.home, name='home'),
    # Обработка запросов погоды (GET для недавних городов, POST для формы)
    path('weather/', views.get_weather, name='get_weather'),
    # API для автодополнения городов (с отключением CSRF для AJAX)
    path(
        'autocomplete/',
        csrf_exempt(views.autocomplete),
        name='autocomplete',
    ),
    # API для получения истории поиска (JSON)
    path(
        'api/search-history/',
        csrf_exempt(views.search_history_api),
        name='search_history_api',
    ),
    # API для получения статистики по городам (JSON)
    path(
        'api/search-stats/',
        csrf_exempt(views.search_stats_api),
        name='search_stats_api',
    ),
]
