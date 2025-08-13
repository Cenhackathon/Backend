from rest_framework import serializers
from .models import WeatherCurrentInfo, WeatherFutureInfo

class WeatherCurrentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherCurrentInfo
        fields = '__all__'

class WeatherFutureSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherFutureInfo
        fields = '__all__'

