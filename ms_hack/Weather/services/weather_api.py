import os
import requests
import logging
from datetime import datetime
from django.conf import settings
from ..models import WeatherCurrentInfo, WeatherFutureInfo

# 설정 상수
KMA_API_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
LOCATION_NAME = "동대문구"
LATITUDE = 37.5744
LONGITUDE = 127.0396

# 로깅 설정
logger = logging.getLogger(__name__)

def fetch_weather_from_kma():
    """현재 날씨 정보 가져오기"""
    params = {
        "serviceKey": os.getenv("KMA_API_KEY", settings.KMA_API_KEY),
        "numOfRows": "10",
        "pageNo": "1",
        "dataType": "JSON",
        "base_date": datetime.now().strftime("%Y%m%d"),
        "base_time": "0500",
        "nx": "61",
        "ny": "127"
    }

    try:
        response = requests.get(KMA_API_URL, params=params)
        response.raise_for_status()
        items = response.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
    except Exception as e:
        logger.error(f"[현재 날씨 API 오류] {e}")
        return

    for item in items:
        WeatherCurrentInfo.objects.update_or_create(
            location_name=LOCATION_NAME,
            updated_at=datetime.now(),  # auto_now 필드와 충돌 가능성 있음
            defaults={
                "latitude": LATITUDE,
                "longitude": LONGITUDE,
                "temperature": item.get("TMP", 0),
                "humidity": item.get("REH", 0),
                "wind_speed": item.get("WSD", 0),
                "uv_index": 0.0,
                "weather_condition": item.get("PTY", "맑음"),
            }
        )

def fetch_forecast_for_dongdaemun():
    """미래 날씨 예보 가져오기"""
    params = {
        "serviceKey": os.getenv("KMA_API_KEY", settings.KMA_API_KEY),
        "numOfRows": "1000",
        "pageNo": "1",
        "dataType": "JSON",
        "base_date": datetime.now().strftime("%Y%m%d"),
        "base_time": "0500",
        "nx": "61",
        "ny": "127"
    }

    try:
        response = requests.get(KMA_API_URL, params=params)
        response.raise_for_status()
        items = response.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
    except Exception as e:
        logger.error(f"[미래 날씨 API 오류] {e}")
        return

    forecast_data = {}
    for item in items:
        fcst_time = item.get('fcstDate', '') + item.get('fcstTime', '')
        if not fcst_time:
            continue
        forecast_data.setdefault(fcst_time, {})[item['category']] = item['fcstValue']

    for fcst_time, data in forecast_data.items():
        try:
            dt = datetime.strptime(fcst_time, "%Y%m%d%H%M")
            if dt < datetime.now():
                continue  # 과거 데이터는 저장하지 않음
            save_forecast(dt, data)
        except Exception as e:
            logger.error(f"[예보 저장 오류] {fcst_time}: {e}")

def save_forecast(dt, data):
    """예보 데이터 저장 함수"""
    WeatherFutureInfo.objects.update_or_create(
        location_name=LOCATION_NAME,
        time_set=dt,
        defaults={
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "temperature": data.get("TMP", 0),
            "humidity": data.get("REH", 0),
            "wind_speed": data.get("WSD", 0),
            "uv_index": 0.0,  # 별도 API 필요
            "weather_condition": data.get("PTY", "맑음"),
        }
    )
