import firebase_admin
from firebase_admin import credentials, messaging
import os
from decouple import config
from ..models import UserDeviceToken

FIREBASE_CRED_PATH = config("GOOGLE_APPLICATION_CREDENTIALS")

def send_push_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token
    )
    try:
        response = messaging.send(message)
        return 200, {"firebase_response": response}
    except Exception as e:
        # ✅ 특정 에러 메시지에 따라 토큰 제거
        if "registration-token-not-registered" in str(e).lower() or "invalid" in str(e).lower():
            UserDeviceToken.objects.filter(fcm_token=token).delete()
        return None, {"error": str(e)}