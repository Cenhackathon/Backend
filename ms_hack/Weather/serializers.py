from rest_framework import serializers
from .models import WeatherCurrentInfo, WeatherFutureInfo

class WeatherCurrentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherCurrentInfo
        fields = [
            "weather_id",
            "location_name",
            "latitude",
            "longitude",
            "temperature",
            "humidity",
            "wind_speed",
            "uv_index",
            "weather_condition",
            "updated_at"
        ]

class WeatherFutureSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherFutureInfo
        fields = [
            "weather_id",
            "location_name",
            "latitude",
            "longitude",
            "temperature",
            "humidity",
            "wind_speed",
            "uv_index",
            "weather_condition",
            "time_set"
