from django.conf import settings
from django.db import models
from django.utils import timezone
from decimal import Decimal

# 경고 알림 모델
class AlertLog(models.Model):
    alert_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=100, default="동대문구")
    alert_type = models.CharField(max_length=50, null=True, blank=True)
    alert_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    send_status = models.BooleanField(default=False)  # 성공 여부
    send_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Alert {self.alert_id} - {self.location_name}"
    
# 현재 날씨
class WeatherCurrentInfo(models.Model):
    weather_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=100, default="동대문구")
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    uv_index = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    weather_condition = models.CharField(max_length=50, null=True, blank=True)
    time_set = models.DateTimeField(default=timezone.now)  # 추가됨
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.location_name} - {self.weather_condition or '정보 없음'}"
    
# 미래 날씨
class WeatherFutureInfo(models.Model):
    weather_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=100, default="동대문구")
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    uv_index = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    weather_condition = models.CharField(max_length=50, null=True, blank=True)
    time_set = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.location_name} - {self.time_set.strftime('%Y-%m-%d %H:%M')}"

# 사용자 디바이스 토큰 (FCM 등) 
class UserDeviceToken(models.Model):
    user_id = models.IntegerField()
    fcm_token = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)  # ✅ 추가

    def __str__(self):
        return f"User {self.user_id} - Token"