import os
import requests
import logging
from django.conf import settings
from google.oauth2 import service_account
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

# 🔹 FCM v1 URL
FCM_V1_URL = f"https://fcm.googleapis.com/v1/projects/{os.getenv('FIREBASE_PROJECT_ID')}/messages:send"

# 🔹 Legacy FCM URL
FCM_LEGACY_URL = "https://fcm.googleapis.com/fcm/send"

# ✅ OAuth2 토큰 생성 (FCM v1용)
def get_access_token():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=["https://www.googleapis.com/auth/firebase.messaging"]
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        logger.error(f"[FCM OAuth2 오류] {e}")
        return None

# ✅ FCM v1 방식 푸시 전송
def send_push_v1(token, title, body):
    access_token = get_access_token()
    if not access_token:
        return None, {"error": "Access token 생성 실패"}

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
        logger.error(f"[FCM Legacy 전송 오류] {e}")
        return None, {"error": str(e)}