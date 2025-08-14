import logging
from datetime import datetime, timedelta
from ..models import WeatherFutureInfo, AlertLog, UserDeviceToken
from .fcm_helper import send_push_notification

# 설정 상수
THRESHOLD_TEMP = 35.0
THRESHOLD_UV = 7.0
THRESHOLD_WIND = 15.0
DEFAULT_LOCATION = "동대문구"

logger = logging.getLogger(__name__)

def check_weather_alerts(user_id=1, location=DEFAULT_LOCATION):
    now = datetime.now()
    one_week_later = now + timedelta(days=7)

    forecasts = WeatherFutureInfo.objects.filter(
        location_name=location,
        time_set__range=[now, one_week_later]
    )

    try:
        token = UserDeviceToken.objects.get(user_id=user_id).fcm_token
    except UserDeviceToken.DoesNotExist:
        logger.warning(f"[FCM 토큰 없음] user_id={user_id}")
        token = None

    for forecast in forecasts:
        alerts = generate_alert_messages(forecast)

        for msg in alerts:
            if not is_alert_logged(user_id, msg, forecast.time_set.date()):
                AlertLog.objects.create(
                    user_id=user_id,
                    alert_type="system",
                    message=msg,
                    read_status=False
                )
                if token:
                    send_push_notification(token, "날씨 경고", msg)

def generate_alert_messages(forecast):
    """예보 데이터를 기반으로 경고 메시지 생성"""
    messages = []
    if forecast.temperature >= THRESHOLD_TEMP:
        messages.append(f"폭염 주의: 기온 {forecast.temperature}°C")
    if forecast.uv_index >= THRESHOLD_UV:
        messages.append(f"자외선 주의: 지수 {forecast.uv_index}")
    if forecast.wind_speed >= THRESHOLD_WIND:
        messages.append(f"강풍 주의: 풍속 {forecast.wind_speed}m/s")
    return messages

def is_alert_logged(user_id, message, date):
    """이미 해당 날짜에 동일 메시지가 기록되었는지 확인"""
    return AlertLog.objects.filter(
        user_id=user_id,
        message=message,
        alert_type="system",
        created_at__date=date
    ).exists()
