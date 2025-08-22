from shelter.models import HeatShelter
from Weather.models import WeatherFutureInfo, UserDeviceToken, AlertLog
from .fcm_helper import send_push_notification
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 🔹 혼잡도 분류 함수
def classify_congestion(current_count, capacity):
    ratio = current_count / capacity
    if ratio < 0.4:
        return "여유"
    elif ratio < 0.8:
        return "보통"
    else:
        return "혼잡"

# 🔹 폭염 위험 및 쉼터 알림 체크 함수
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
            # 🔹 혼잡도 계산
            congestion = classify_congestion(shelter.current_count, shelter.capacity)

            # 🔹 메시지 구성
            msg = (
                f"{shelter.name} 근처 폭염 위험!\n"
                f"기온: {forecast.temperature}°C\n"
                f"현재 인원: {shelter.current_count}명\n"
                f"수용 인원: {shelter.capacity}명\n"
                f"혼잡도: {congestion}"
            )

            # 🔹 중복 알림 방지
            if not AlertLog.objects.filter(
                user_id=user_id,
                alert_message=msg,
                alert_type="shelter",
                created_at__date=datetime.now().date()
            ).exists():
                AlertLog.objects.create(
                    user_id=user_id,
                    location_name=shelter.road_address,
                    alert_type="shelter",
                    alert_message=msg,
                    read_status=False
                )

                # 🔹 FCM 푸시 알림 전송
                if token:
                    status, result = send_push_notification(token, "쉼터 경고", msg)
                    if status == 200:
                        logger.info(f"[FCM 전송 성공] {msg}")
                    else:
                        logger.warning(f"[FCM 전송 실패] {result}")

            # 🔹 알림 정보 저장
            alerts.append({
                "shelter": shelter.name,
                "address": shelter.road_address,
                "temperature": forecast.temperature,
                "time": forecast.time_set,
                "current_count": shelter.current_count,
                "capacity": shelter.capacity,
                "congestion": congestion,
                "risk": "폭염 위험"
            })

    return alerts