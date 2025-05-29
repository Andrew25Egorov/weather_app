from urllib.parse import quote

import requests
from django.core.cache import cache

from .constants import WEATHER_CODES


def get_city_coordinates(city_name):
    """
    Получает координаты города через API геокодирования
    Возвращает словарь с ключами: latitude, longitude, country
    """
    # Создаем безопасный ключ для кэша
    safe_city_name = quote(city_name.lower().replace(' ', '_'))
    cache_key = f'city_coords_{safe_city_name}'

    # Проверяем кэш
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    # Пробуем Open-Meteo Geocoding API
    data = try_openmeteo_geocoding(city_name)
    if data:
        cache.set(cache_key, data, timeout=60 * 60 * 24)  # Кэшируем на 1 день
        return data

    # Если Open-Meteo не сработал, пробуем Nominatim (резервный вариант)
    data = try_nominatim_geocoding(city_name)
    if data:
        cache.set(cache_key, data, timeout=60 * 60 * 24)
        return data

    return None


def try_openmeteo_geocoding(city_name):
    """Попытка получить координаты через Open-Meteo API"""
    url = (f'https://geocoding-api.open-meteo.com/v1/'
           f'search?name={city_name}&count=1')

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get('results'):
            city = data['results'][0]
            return {
                'latitude': city['latitude'],
                'longitude': city['longitude'],
                'country': city.get('country', ''),
            }
    except requests.RequestException as e:
        print(f'OpenMeteo Geocoding error: {e}')

    return None


def try_nominatim_geocoding(city_name):
    """Резервный геокодер через Nominatim (OpenStreetMap)"""
    url = (
        f'https://nominatim.openstreetmap.org/'
        f'search?q={city_name}&format=json&limit=1'
    )

    try:
        response = requests.get(url,
                                headers={'User-Agent': 'WeatherApp'},
                                timeout=5)
        response.raise_for_status()
        data = response.json()

        if data:
            return {
                'latitude': float(data[0]['lat']),
                'longitude': float(data[0]['lon']),
                'country': extract_country_from_nominatim(data[0]),
            }
    except requests.RequestException as e:
        print(f'Nominatim Geocoding error: {e}')

    return None


def extract_country_from_nominatim(result):
    """Извлекает название страны из Nominatim response"""
    display_name = result.get('display_name', '')
    parts = [part.strip() for part in display_name.split(',')]
    return parts[-1] if parts else ''


def format_weather_data(api_data, city_name, country=''):
    """
    Форматирует сырые данные от погодного API в удобный
    для отображения формат
    """
    current = api_data['current_weather']
    hourly = api_data['hourly']

    weather_info = WEATHER_CODES.get(
        current['weathercode'], {'desc': 'Неизвестно', 'icon': '❓'}
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
            'precipitation': hourly.get('precipitation_probability', [])[:24],
        },
    }
