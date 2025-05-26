from django.contrib.auth import views
from django.urls import path
from . import views
from .apps import WeatherConfig
from .views import WeatherView, SearchHistoryView, city_autocomplete, IndexView, UserRegistrationView

app_name = WeatherConfig.name

urlpatterns = [
    # path('', views.home, name='home'),
    path('index/', IndexView.as_view(), name='index'),
    path('', UserRegistrationView.as_view(), name='register'),
    path('weather/', WeatherView.as_view(), name='weather'),
    path('history/', SearchHistoryView.as_view(), name='history'),
    path('city-autocomplete/', city_autocomplete, name='city-autocomplete'),
]
