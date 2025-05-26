from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

class WeatherAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.client.login(username='testuser', password='pass')

    def test_weather_api(self):
        response = self.client.get('/api/weather/', {'city': 'Berlin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('temperature', response.data)

    def test_history_api(self):
        self.client.get('/api/weather/', {'city': 'Berlin'})
        response = self.client.get('/api/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
