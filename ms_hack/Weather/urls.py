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
    path('forecast/', WeatherForecastView.as_view()),
    path('forecast/create/', CreateForecastWithOffsetView.as_view()),
    path('update/', WeatherUpdateView.as_view()),
    path('alert/user/', UserWeatherAlertView.as_view()),
    path('alert/shelter/', ShelterWeatherAlertView.as_view()),
    path('alert/trigger/', WeatherAlertTriggerView.as_view()),  # ✅ 연결 완료
]