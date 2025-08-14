import os
import requests
import logging
from django.conf import settings

# 로깅 설정
logger = logging.getLogger(__name__)

# FCM 서버 URL
FCM_URL = "https://fcm.googleapis.com/fcm/send"

def send_push_notification(token, title, body):
    """FCM 푸시 알림 전송 함수"""
    server_key = os.getenv("FCM_SERVER_KEY", settings.FCM_SERVER_KEY)
    if not server_key:
        logger.error("[FCM 오류] 서버 키가 설정되지 않았습니다.")
        return None, {"error": "Missing FCM server key"}

    headers = {
        "Authorization": f"key={server_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": token,
        "notification": {
            "title": title,
            "body": body
        },
        "priority": "high"
    }

    try:
        response = requests.post(FCM_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.status_code, response.json()
    except requests.RequestException as e:
        logger.error(f"[FCM 전송 오류] {e}")
        return None, {"error": str(e)}

