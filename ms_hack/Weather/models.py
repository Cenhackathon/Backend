from django.conf import settings
from django.db import models
from django.utils import timezone

# 경고 알림 모델
class AlertLog(models.Model):
    alert_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=100, default="동대문구")
    alert_type = models.CharField(max_length=50, null=True, blank=True)
    alert_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert {self.alert_id} - {self.location_name}"

# 현재 날씨
class WeatherCurrentInfo(models.Model):
    weather_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=100, default="동대문구")
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    temperature = models.DecimalField(max_digits=4, decimal_places=1)
    humidity = models.DecimalField(max_digits=4, decimal_places=1)
    wind_speed = models.DecimalField(max_digits=4, decimal_places=1)
    uv_index = models.DecimalField(max_digits=3, decimal_places=1)
    weather_condition = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)  # 저장 시 자동 갱신

    def __str__(self):
        return f"{self.location_name} - {self.weather_condition}"

# 미래 날씨
class WeatherFutureInfo(models.Model):
    weather_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=100, default="동대문구")
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    temperature = models.DecimalField(max_digits=4, decimal_places=1)
    humidity = models.DecimalField(max_digits=4, decimal_places=1)
    wind_speed = models.DecimalField(max_digits=4, decimal_places=1)
    uv_index = models.DecimalField(max_digits=3, decimal_places=1)
    weather_condition = models.CharField(max_length=50)
    time_set = models.DateTimeField(default=timezone.now)  # 예측 시간 (프론트에서 hour_offset 기반으로 계산)

    def __str__(self):
        return f"{self.location_name} - {self.time_set.strftime('%Y-%m-%d %H:%M')}"


class UserDeviceToken(models.Model):
    user_id = models.IntegerField()
    fcm_token = models.CharField(max_length=255)

    def __str__(self):
        return f"User {self.user_id} - Token"