from shelter.models import HeatShelter
from Weather.models import WeatherFutureInfo, UserDeviceToken, AlertLog
from .fcm_helper import send_push_notification
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def check_shelter_weather_risks(user_id=1, threshold=33):
    alerts = []
    shelters = HeatShelter.objects.all()
    try:
        token = UserDeviceToken.objects.get(user_id=user_id).fcm_token
    except UserDeviceToken.DoesNotExist:
        logger.warning(f"[FCM 토큰 없음] user_id={user_id}")
        token = None

    forecast = WeatherFutureInfo.objects.filter(
        location_name__icontains="동대문구"
    ).order_by('-time_set').first()

    if forecast and forecast.temperature > threshold:
        for shelter in shelters:
            msg = f"{shelter.name} 근처 폭염 위험! 기온: {forecast.temperature}°C"

            # 중복 알림 방지
            if not AlertLog.objects.filter(
                user_id=user_id,
                message=msg,
                alert_type="shelter",
                created_at__date=datetime.now().date()
            ).exists():
                AlertLog.objects.create(
                    user_id=user_id,
                    alert_type="shelter",
                    message=msg,
                    read_status=False
                )
                if token:
                    status, result = send_push_notification(token, "쉼터 경고", msg)
                    if status == 200:
                        logger.info(f"[FCM 전송 성공] {msg}")
                    else:
                        logger.warning(f"[FCM 전송 실패] {result}")

            alerts.append({
                "shelter": shelter.name,
                "address": shelter.road_address,
                "temperature": forecast.temperature,
                "time": forecast.time_set,
                "risk": "폭염 위험"
            })

    return alerts