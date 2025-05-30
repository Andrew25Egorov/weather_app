from urllib.parse import quote, unquote

import requests
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_str
from django.views.decorators.csrf import csrf_exempt

from .constants import WEATHER_CODES, API_TIMEOUT, CACHE_TIMEOUT


def home(request):
    recent_city = unquote(request.COOKIES.get('recent_city', ''))
    error = request.GET.get('error', '')
    return render(request, 'weather/home.html', {
        'recent_city': recent_city,
        'error': error
    })


def get_weather(request):
    city_name = get_city_from_request(request)
    if not city_name:
        return redirect('home')

    coords = get_city_coordinates(city_name)
    if not coords:
        return redirect_with_error(
            request,
            (f"\u0413\u043e\u0440\u043e\u0434 '{city_name}' \u043d\u0435"
             f"\u043d\u0430\u0439\u0434\u0435\u043d")
        )

    weather_data = fetch_weather_data(coords['latitude'], coords['longitude'])
    if not weather_data:
        return redirect_with_error(
            request,
            '\u041e\u0448\u0438\u0431\u043a\u0430 \u043f\u043e\u043b\u0443\
            u0447\u0435\u043d\u0438\u044f \u0434\u0430\u043d\u043d\u044b\
            u0445 \u043e \u043f\u043e\u0433\u043e\u0434\u0435'
        )

    result = format_weather_data(city_name, coords, weather_data)

    response = render(request, 'weather/result.html', {
        'weather': result,
        'hourly_forecast': zip(
            result['hourly']['time'][:12],
            result['hourly']['temperature'][:12],
            result['hourly']['windspeed'][:12],
            result['hourly']['winddirection'][:12]
        )
    })
    response.set_cookie('recent_city', quote(city_name), max_age=CACHE_TIMEOUT)
    return response


@csrf_exempt
def autocomplete(request):
    if 'term' not in request.GET:
        return JsonResponse([], safe=False)

    term = request.GET.get('term', '').strip()
    if len(term) < 2:
        return JsonResponse([], safe=False)

    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': term,
            'format': 'json',
            'accept-language': 'ru',
            'addressdetails': 1,
            'limit': 5
        }
        headers = {'User-Agent': 'YourWeatherApp/1.0 (your@email.com)'}

        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        suggestions = []
        for item in data:
            address = item.get('address', {})
            city = (
                address.get('city')
                or address.get('town')
                or address.get('village')
                or address.get('municipality')
                or item.get('display_name', '').split(',')[0]
            )
            country = address.get('country', '')

            if city and country:
                suggestions.append(f"{city.strip()}, {country.strip()}")

        return JsonResponse(suggestions, safe=False,
                            json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        print(f"Autocomplete error: {str(e)}")
        return JsonResponse([],
                            safe=False,
                            status=500,
                            json_dumps_params={'ensure_ascii': False})


def get_city_from_request(request):
    if request.method == 'POST':
        return request.POST.get('city', '').strip()
    elif request.method == 'GET':
        return request.GET.get('city', '').strip()
    return None


def get_city_coordinates(city_name):
    cache_key = f"coords_{city_name.lower().replace(' ', '_')}"
    if cached := cache.get(cache_key):
        return cached

    url = (f"https://nominatim.openstreetmap.org/search?q={city_name}&format="
           f"json&addressdetails=1&accept-language=ru")
    headers = {'User-Agent': 'WeatherApp'}
    try:
        response = requests.get(url, headers=headers, timeout=API_TIMEOUT)
        data = response.json()
        if data:
            coords = {
                'latitude': float(data[0]['lat']),
                'longitude': float(data[0]['lon']),
                'country': data[0].get('address', {}).get('country', '')
            }
            cache.set(cache_key, coords, timeout=CACHE_TIMEOUT)
            return coords
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None


def fetch_weather_data(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&"
        "current_weather=true&"
        "hourly=temperature_2m,weathercode,windspeed_10m,winddirection_10m&"
        "windspeed_unit=ms&timezone=auto"
    )
    try:
        response = requests.get(url, timeout=API_TIMEOUT)
        return response.json()
    except Exception as e:
        print(f"Weather API error: {e}")
        return None


def format_weather_data(city_name, coords, api_data):
    city, country = parse_city_name(city_name)
    current = api_data['current_weather']
    hourly = api_data['hourly']
    weather_info = WEATHER_CODES.get(current['weathercode'],
                                     {'desc': 'Неизвестно', 'icon': '❓'})

    return {
        'city': city,
        'country': country or coords.get('country', ''),
        'current': {
            'temperature': current['temperature'],
            'windspeed': current['windspeed'],
            'winddirection': current['winddirection'],
            'time': current['time'],
            'description': weather_info['desc'],
            'icon': weather_info['icon']
        },
        'hourly': {
            'time': hourly['time'],
            'temperature': hourly['temperature_2m'],
            'windspeed': hourly['windspeed_10m'],
            'winddirection': hourly['winddirection_10m']
        }
    }


def parse_city_name(full_name):
    parts = [p.strip() for p in full_name.split(',', 1)]
    return (parts[0], parts[1]) if len(parts) > 1 else (parts[0], '')


def redirect_with_error(request, error_msg):
    return redirect(f"{reverse('home')}?error={force_str(error_msg)}")
