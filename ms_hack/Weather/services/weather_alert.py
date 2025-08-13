from datetime import datetime, timedelta
from ..models import WeatherFutureInfo, AlertLog, UserDeviceToken
from .fcm_helper import send_push_notification

def check_weather_alerts(user_id=1, location="동대문구"):
    threshold_temp = 35.0
    threshold_uv = 7.0
    threshold_wind = 15.0

    now = datetime.now()
    one_week_later = now + timedelta(days=7)

    forecasts = WeatherFutureInfo.objects.filter(
        location_name=location,
        time_set__range=[now, one_week_later]
    )

    try:
        token = UserDeviceToken.objects.get(user_id=user_id).fcm_token
    except UserDeviceToken.DoesNotExist:
        token = None

    for forecast in forecasts:
        alerts = []

        if forecast.temperature >= threshold_temp:
            alerts.append(f"폭염 주의: 기온 {forecast.temperature}°C")
        if forecast.uv_index >= threshold_uv:
            alerts.append(f"자외선 주의: 지수 {forecast.uv_index}")
        if forecast.wind_speed >= threshold_wind:
            alerts.append(f"강풍 주의: 풍속 {forecast.wind_speed}m/s")

        for msg in alerts:
            if not AlertLog.objects.filter(
                user_id=user_id,
                message=msg,
                alert_type="system",
                created_at__date=forecast.time_set.date()
            ).exists():
                AlertLog.objects.create(
                    user_id=user_id,
                    alert_type="system",
                    message=msg,
                    read_status=False
                )
                if token:
                    send_push_notification(token, "날씨 경고", msg)
