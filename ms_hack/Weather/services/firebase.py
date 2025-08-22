import firebase_admin
from firebase_admin import credentials, messaging
import os
from decouple import config

FIREBASE_CRED_PATH = config("GOOGLE_APPLICATION_CREDENTIALS")

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)

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
        return None, {"error": str(e)}