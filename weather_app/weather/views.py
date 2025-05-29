from datetime import datetime

import requests
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

# from django.conf import settings
# import json
from .constants import WEATHER_CODES


def home(request):
    """
    Главная страница с формой поиска.
    Показывает последний просмотренный город и историю поиска.
    """
    context = {
        'recent_city': request.COOKIES.get('recent_city', ''),
        'search_history': request.session.get('search_history', [])[:3],
    }
    return render(request, 'weather/home.html', context)


def get_weather(request):
    """
    Обработчик запросов погоды. Работает с GET и POST запросами.
    GET - для ссылки 'Recently viewed'
    POST - для основной формы поиска
    """
    if request.method == 'POST':
        city_name = request.POST.get('city', '').strip()
    elif request.method == 'GET' and 'city' in request.GET:
        city_name = request.GET.get('city').strip()
    else:
        return redirect('home')

    if not city_name:
        return render_weather_error(request, 'Please enter a city name')

    # if request.method == 'POST':
    #     city_name = request.POST.get('city', '').strip()
    #     if not city_name:
    #         return redirect('home')

    #     # Сохраняем в сессии
    #     history = request.session.get('search_history', [])
    #     if city_name not in history:
    #         history.insert(0, city_name)
    #         request.session['search_history'] = history[:5]

    # Разделяем город и страну (если есть в autocomplete)
    city_parts = [part.strip() for part in city_name.split(',', 1)]
    city = city_parts[0]
    country = city_parts[1] if len(city_parts) > 1 else ''

    # Получаем координаты города
    coords = get_city_coordinates(city)
    if not coords:
        return render_weather_error(request, f"City '{city}' not found")

    # Добавляем страну если она была указана
    if country:
        coords['country'] = country

    # Получаем данные о погоде
    weather_data = fetch_weather_data(coords['latitude'], coords['longitude'])
    if not weather_data:
        return render_weather_error(request, 'Error fetching weather data')

    # Форматируем данные для отображения
    formatted_data = format_weather_data(
        weather_data,
        city_name=city,
        country=coords.get('country', '')
    )

    # Обновляем историю поиска
    update_search_history(request,
                          f"{city},{coords.get('country', '')}".strip(', '))

    # Сохраняем в куках последний город
    response = render(request, 'weather/result.html', {
        'weather': formatted_data,
        'search_history': request.session.get('search_history', [])[:5]
    })
    response.set_cookie('recent_city', city_name, max_age=30 * 24 * 60 * 60)
    return response


@csrf_exempt
def autocomplete(request):
    """
    API для автодополнения городов.
    Возвращает JSON с вариантами городов.
    """
    if 'term' in request.GET:
        term = request.GET.get('term').strip()
        if len(term) < 2:
            return JsonResponse([], safe=False)

        url = (f'https://geocoding-api.open-meteo.com/v1/'
               f'search?name={term}&count=5')

        try:
            response = requests.get(url, timeout=3)
            data = response.json()
            suggestions = [
                f"{city['name']}, {city.get('country', '')}"
                for city in data.get('results', [])
            ]
            return JsonResponse(suggestions, safe=False)
        except Exception:
            return JsonResponse([], safe=False)

    return JsonResponse([], safe=False)


@csrf_exempt
def search_history_api(request):
    """
    API для получения истории поиска текущего пользователя.
    Возвращает JSON с последними 10 запросами.
    """
    history = request.session.get('search_history', [])
    return JsonResponse(history[:10], safe=False)


@csrf_exempt
def search_stats_api(request):
    """
    API для получения статистики по популярным городам.
    Возвращает JSON с городами и количеством запросов.
    """
    from collections import defaultdict
    history = request.session.get('search_history', [])

    stats = defaultdict(int)
    for item in history:
        stats[item['city']] += 1

    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    return JsonResponse(dict(sorted_stats[:10]))


# Вспомогательные функции
def fetch_weather_data(latitude, longitude):
    """Получение данных о погоде из Open-Meteo API"""
    url = (
        f'https://api.open-meteo.com/v1/forecast?'
        f'latitude={latitude}&longitude={longitude}&'
        'current_weather=true&'
        'hourly=temperature_2m,relativehumidity_2m,weathercode,windspeed_10m'
    )

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f'Weather API error: {e}')
        return None


def update_search_history(request, city_name):
    """Обновление истории поиска в сессии"""
    if 'search_history' not in request.session:
        request.session['search_history'] = []

    history = request.session['search_history']

    # Удаляем дубликаты
    history = [item for item in history if item['city'] != city_name]

    # Добавляем новый поиск
    history.insert(0, {
        'city': city_name,
        'timestamp': datetime.now().isoformat()
    })

    # Сохраняем только последние 10 записей
    request.session['search_history'] = history[:10]
    request.session.modified = True


def render_weather_error(request, error_message):
    """Рендеринг страницы с ошибкой"""
    return render(request, 'weather/home.html', {
        'error': error_message,
        'recent_city': request.COOKIES.get('recent_city'),
        'search_history': request.session.get('search_history', [])[:5]
    })


def format_weather_data(data, city_name, country):
    """Форматирование данных о погоде для отображения"""
    current = data['current_weather']
    hourly = data['hourly']

    weather_info = WEATHER_CODES.get(
        current['weathercode'],
        {'desc': 'Unknown', 'icon': '❓'}
    )

    return {
        'city': city_name,
        'country': country,
        'current': {
            'time': current['time'],
            'temperature': current['temperature'],
            'windspeed': current['windspeed'],
            'weather_desc': weather_info['desc'],
            'weather_icon': weather_info['icon'],
        },
        'hourly': {
            'time': hourly['time'][:24],
            'temperature': hourly['temperature_2m'][:24],
            'humidity': hourly['relativehumidity_2m'][:24],
        }
    }


def get_city_coordinates(city_name):
    """Получение координат города через Open-Meteo Geocoding API"""
    safe_name = city_name.lower().replace(' ', '_')
    cache_key = f'city_coords_{safe_name}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    url = (f'https://geocoding-api.open-meteo.com/v1/'
           f'search?name={city_name}&count=1')

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get('results'):
            city = data['results'][0]
            result = {
                'latitude': city['latitude'],
                'longitude': city['longitude'],
                'country': city.get('country', '')
            }
            cache.set(cache_key, result, timeout=60 * 60 * 24)
            # Кэш на 1 день
            return result
    except Exception as e:
        print(f'Geocoding error: {e}')

    return None
