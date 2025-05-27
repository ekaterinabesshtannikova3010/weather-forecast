from django.shortcuts import render
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import CitySearch
from .serializers import CitySearchSerializer
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django import forms


# def home(request):
#     return render(request, 'weather/index.html')

class IndexView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return render(request, 'weather/index.html')


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")

class UserRegistrationView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'weather/register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно.')
            return redirect('weather:index')

        return render(request, 'weather/register.html', {'form': form})

class WeatherView(APIView):
    permission_classes = [IsAuthenticated]
    model = CitySearch
    template_name = 'weather/index.html'
    success_url = reverse_lazy('weather:index')

    def get(self, request):
        city = request.query_params.get('city', None)  # Default to None if not provided
        if not city:
            return Response({"message": "Город не указан, будет использован город по умолчанию."}, status=200)

        city_search_record = self._get_or_create_city_search_record(request.user, city)
        self._increment_search_count_if_needed(city_search_record)

        geo_data = self._get_geographical_data(city)
        if not geo_data:
            return self._error_response("Город не найден", 404)

        weather_data = self._get_weather_data(geo_data['latitude'], geo_data['longitude'])
        if not weather_data:
            return self._error_response("Ошибка API погоды", 500)

        return Response(self._format_weather_response(city, weather_data))

    def _error_response(self, message, status_code):
        return Response({"error": message}, status=status_code)

    def _get_or_create_city_search_record(self, user, city_name):
        obj, created = CitySearch.objects.get_or_create(user=user, city_name=city_name)
        return obj

    def _increment_search_count_if_needed(self, city_search_record):
        city_search_record.search_count += 1
        city_search_record.save()

    def _get_geographical_data(self, city):
        geo_resp = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1")
        if geo_resp.status_code == 200 and geo_resp.json().get('results'):
            return geo_resp.json()['results'][0]
        return None

    def _get_weather_data(self, latitude, longitude):
        weather_resp = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true")
        if weather_resp.status_code == 200:
            return weather_resp.json()['current_weather']
        return None

    def _format_weather_response(self, city, weather_data):
        return {
            "city": city,
            "temperature": weather_data['temperature'],
            "windspeed": weather_data['windspeed'],
            "weathercode": weather_data['weathercode'],
            "time": weather_data['time'],
        }
# class WeatherView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         city = request.query_params.get('city')
#         if not city:
#             return Response({"error": "Параметр город является обязательным"}, status=400)
#
#         # Сохраняем или обновляем историю поиска
#         obj, created = CitySearch.objects.get_or_create(user=request.user, city_name=city)
#         if not created:
#             obj.search_count += 1
#             obj.save()
#
#         # Получаем координаты города (для простоты используем open-meteo geocoding API)
#         geo_resp = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1")
#         if geo_resp.status_code != 200 or not geo_resp.json().get('results'):
#             return Response({"error": "City not found"}, status=404)
#         geo_data = geo_resp.json()['results'][0]
#         lat = geo_data['latitude']
#         lon = geo_data['longitude']
#
#         # Запрос погоды
#         weather_resp = requests.get(
#             f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
#         )
#         if weather_resp.status_code != 200:
#             return Response({"error": "Weather API error"}, status=500)
#
#         weather_data = weather_resp.json()['current_weather']
#         return Response({
#             "city": city,
#             "temperature": weather_data['temperature'],
#             "windspeed": weather_data['windspeed'],
#             "weathercode": weather_data['weathercode'],
#             "time": weather_data['time'],
#         })


class SearchHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        searches = CitySearch.objects.filter(user=request.user).order_by('-last_searched')
        serializer = CitySearchSerializer(searches, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def city_autocomplete(request):
    query = request.query_params.get('q', '')
    if not query:
        return Response([])

    geo_resp = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5")
    if geo_resp.status_code != 200:
        return Response([], status=500)
    results = geo_resp.json().get('results', [])
    cities = [res['name'] for res in results]
    return Response(cities)
