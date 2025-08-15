from django.urls import path
from .views import (
    WeatherUpdateView,
    WeatherForecastView,
    CreateForecastWithOffsetView,
    UserWeatherAlertView,
    ShelterWeatherAlertView
)

urlpatterns = [
    path("weather/update/", WeatherUpdateView.as_view(), name="weather-update"),
    path("weather/forecast/", WeatherForecastView.as_view(), name="weather-forecast"),
    path("weather/forecast/create/", CreateForecastWithOffsetView.as_view(), name="create-forecast-offset"),
    path("weather/alert/user/", UserWeatherAlertView.as_view(), name="user-weather-alert"),       # 사용자 기반 알림
    path("weather/alert/shelter/", ShelterWeatherAlertView.as_view(), name="shelter-weather-alert") # 쉼터 기반 위험 분석
]