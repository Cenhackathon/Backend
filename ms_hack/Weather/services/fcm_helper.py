import requests
import os
from django.conf import settings

def send_push_notification(token, title, body):
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Authorization": f"key={os.getenv('FCM_SERVER_KEY', settings.FCM_SERVER_KEY)}",
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

    response = requests.post(url, json=payload, headers=headers)
    return response.status_code, response.json()
