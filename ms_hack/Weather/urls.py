from django.urls import path
from .views import (
    WeatherUpdateView,
    WeatherForecastView,
    WeatherAlertTriggerView
)

urlpatterns = [
    path("weather/update/", WeatherUpdateView.as_view(), name="weather-update"),
    path("weather/forecast/", WeatherForecastView.as_view(), name="weather-forecast"),
    path("weather/alert/", WeatherAlertTriggerView.as_view(), name="weather-alert"),
]
