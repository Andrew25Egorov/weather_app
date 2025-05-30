from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse


class WeatherAppTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Введите город')

    def test_autocomplete_returns_data(self):
        with patch('weather.views.requests.get') as mock_get:
            mock_get.return_value.json.return_value = [
                {'address': {'city': 'Москва', 'country': 'Россия'},
                 'display_name': 'Москва, Россия'}
            ]
            response = self.client.get(reverse('autocomplete'),
                                       {'term': 'Мос'})
            self.assertEqual(response.status_code, 200)
            self.assertJSONEqual(response.content, ["Москва, Россия"])

    def test_get_weather_redirects_on_invalid_city(self):
        with patch('weather.views.get_city_coordinates', return_value=None):
            response = self.client.get(reverse('get_weather'),
                                       {'city': 'Неведомоград'})
            self.assertRedirects(
                response,
                reverse('home')
                + '?error=%D0%93%D0%BE%D1%80%D0%BE%D0%B4+%27'
                '%D0%9D%D0%B5%D0%B2%D0%B5%D0%B4%D0%BE%D0%BC%D0%BE'
                '%D0%B3%D1%80%D0%B0%D0%B4%27+%D0%BD%D0%B5+%D0%BD%D0%B0'
                '%D0%B9%D0%B4%D0%B5%D0%BD'
            )

    def test_get_weather_success(self):
        with patch('weather.views.get_city_coordinates') as mock_coords, \
             patch('weather.views.fetch_weather_data') as mock_weather:

            mock_coords.return_value = {
                'latitude': 55.75,
                'longitude': 37.61,
                'country': 'Россия'}
            mock_weather.return_value = {
                'current_weather': {
                    'temperature': 12.3,
                    'windspeed': 4.5,
                    'winddirection': 90,
                    'time': '2025-05-30T12:00',
                    'weathercode': 0
                },
                'hourly': {
                    'time': ['2025-05-30T13:00'] * 12,
                    'temperature_2m': [15.0] * 12,
                    'windspeed_10m': [5.0] * 12,
                    'winddirection_10m': [180] * 12
                }
            }
            response = self.client.get(reverse('get_weather'),
                                       {'city': 'Москва'})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Погода: Москва')
