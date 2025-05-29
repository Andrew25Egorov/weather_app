from django.test import TestCase, Client
from django.urls import reverse
from .models import CitySearch
import json


class WeatherAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        CitySearch.objects.create(
            city_name='Test City', country='Test Country', latitude=0.0, longitude=0.0
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Weather Forecast')

    def test_weather_submission(self):
        response = self.client.post(reverse('get_weather'), {'city': 'Paris'})
        self.assertIn(response.status_code, [200, 302])
    # 302 если редирект при ошибке

    def test_search_history_api(self):
        response = self.client.get(reverse('search_history_api'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)

    def test_city_search_model(self):
        city = CitySearch.objects.get(city_name='Test City')
        self.assertEqual(city.country, 'Test Country')
        city.increment_search_count()
        self.assertEqual(city.search_count, 2)
