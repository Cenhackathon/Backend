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

    now = datetime.now()
    target_time = None
    target_data = {}

    for item in items:
        fcst_datetime = datetime.strptime(item['fcstDate'] + item['fcstTime'], "%Y%m%d%H%M")
        # 현재 시각 ±1시간 범위 내 데이터만
        if abs((fcst_datetime - now).total_seconds()) <= 3600:
            target_time = fcst_datetime
            target_data[item['category']] = item['fcstValue']

    if not target_time:
        print("[현재 날씨] 현재 시각에 해당하는 예보 데이터 없음")
        return

    WeatherCurrentInfo.objects.update_or_create(
        location_name="동대문구",
        time_set=target_time,  # 중복 방지 키
        defaults={
            "latitude": 37.5744,
            "longitude": 127.0396,
            "temperature": target_data.get("TMP", 0),
            "humidity": target_data.get("REH", 0),
            "wind_speed": target_data.get("WSD", 0),
            "uv_index": 0.0,
            "weather_condition": target_data.get("PTY", "맑음"),
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

    # 예보 데이터를 시간 단위로 묶기
    forecast_data = {}
    for item in items:
        fcst_time_str = item['fcstDate'] + item['fcstTime']
        if fcst_time_str not in forecast_data:
            forecast_data[fcst_time_str] = {}
        forecast_data[fcst_time_str][item['category']] = item['fcstValue']

    # 각 시간대 데이터 저장 (중복 방지)
    for fcst_time_str, data in forecast_data.items():
        try:
            dt = datetime.strptime(fcst_time_str, "%Y%m%d%H%M")

            WeatherFutureInfo.objects.update_or_create(
                location_name="동대문구",
                time_set=dt,  # 동일 시간대 중복 방지
                defaults={
                    "latitude": 37.5744,
                    "longitude": 127.0396,
                    "temperature": data.get("TMP", 0),
                    "humidity": data.get("REH", 0),
                    "wind_speed": data.get("WSD", 0),
                    "uv_index": 0.0,  # UV 지수는 별도 API 필요
                    "weather_condition": data.get("PTY", "맑음"),
                }
            )
        except Exception as e:
            print(f"[예보 저장 오류] {fcst_time_str}: {e}")


def update_weather_data():
    print("[날씨 업데이트] 현재 날씨 정보 업데이트 시작")
    fetch_weather_from_kma()
    fetch_forecast_for_dongdaemun()
    print("[날씨 업데이트] 현재 날씨 정보 업데이트 완료")
