from django.urls import path
from .views import (
    WeatherUpdateView,
    WeatherForecastView,
    CreateForecastWithOffsetView,
    UserWeatherAlertView,
    ShelterWeatherAlertView,
    WeatherAlertTriggerView,
    CreateForecastWithOffsetView,
)

urlpatterns = [
    path('forecast/', WeatherForecastView.as_view(), name='weather-forecast'),
    path('forecast/create/', CreateForecastWithOffsetView.as_view(), name='weather-forecast-create'),
    path('update/', WeatherUpdateView.as_view(), name='weather-update'),
    path('alert/user/', UserWeatherAlertView.as_view(), name='weather-alert-user'),
    path('alert/shelter/', ShelterWeatherAlertView.as_view(), name='weather-alert-shelter'),
    path('alert/trigger/', WeatherAlertTriggerView.as_view(), name='weather-alert-trigger'),
]

