import os
import requests
import logging
from django.conf import settings
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# 로깅 설정
logger = logging.getLogger(__name__)

# FCM v1 URL
FCM_V1_URL = f"https://fcm.googleapis.com/v1/projects/{os.getenv('FIREBASE_PROJECT_ID')}/messages:send"

def get_access_token():
    """OAuth2 인증 토큰 생성"""
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        scopes=["https://www.googleapis.com/auth/firebase.messaging"]
    )
    credentials.refresh(Request())
    return credentials.token

def send_push_notification(token, title, body):
    """FCM v1 푸시 알림 전송 함수"""
    access_token = get_access_token()
    if not access_token:
        logger.error("[FCM 오류] 액세스 토큰 생성 실패")
        return None, {"error": "Failed to get access token"}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; UTF-8"
    }

    payload = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body
            }
        }
    }

    try:
        response = requests.post(FCM_V1_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.status_code, response.json()
    except requests.RequestException as e:
        logger.error(f"[FCM 전송 오류] {e}")
        return None, {"error": str(e)}

