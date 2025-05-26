from rest_framework import serializers
from .models import CitySearch

class CitySearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CitySearch
        fields = ['city_name', 'search_count', 'last_searched']
