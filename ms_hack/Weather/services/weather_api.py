import os
import requests
from datetime import datetime
from django.conf import settings
from ..models import WeatherCurrentInfo, WeatherFutureInfo

# 현재 날씨 정보 가져오기
def fetch_weather_from_kma():
    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        "serviceKey": os.getenv("KMA_API_KEY", settings.KMA_API_KEY),
        "numOfRows": "10",
        "pageNo": "1",
        "dataType": "JSON",
        "base_date": datetime.now().strftime("%Y%m%d"),
        "base_time": "0500",
        "nx": "61",  # 동대문구 X
        "ny": "127"  # 동대문구 Y
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        items = response.json()['response']['body']['items']['item']
    except Exception as e:
        print(f"[현재 날씨 API 오류] {e}")
        return

    for item in items:
        WeatherCurrentInfo.objects.update_or_create(
            location_name="동대문구",
            updated_at=datetime.now(),  # auto_now로 인해 중복 방지 어려움 → 조건 조정 가능
            defaults={
                "latitude": 37.5744,
                "longitude": 127.0396,
                "temperature": item.get("TMP", 0),
                "humidity": item.get("REH", 0),
                "wind_speed": item.get("WSD", 0),
                "uv_index": 0.0,
                "weather_condition": item.get("PTY", "맑음"),
            }
        )

# 미래 날씨 예보 가져오기
def fetch_forecast_for_dongdaemun():
    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
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
        response = requests.get(url, params=params)
        response.raise_for_status()
        items = response.json()['response']['body']['items']['item']
    except Exception as e:
        print(f"[미래 날씨 API 오류] {e}")
        return

    forecast_data = {}
    for item in items:
        fcst_time = item['fcstDate'] + item['fcstTime']
        if fcst_time not in forecast_data:
            forecast_data[fcst_time] = {}
        forecast_data[fcst_time][item['category']] = item['fcstValue']

    for fcst_time, data in forecast_data.items():
        try:
            dt = datetime.strptime(fcst_time, "%Y%m%d%H%M")
            WeatherFutureInfo.objects.update_or_create(
                location_name="동대문구",
                time_set=dt,
                defaults={
                    "latitude": 37.5744,
                    "longitude": 127.0396,
                    "temperature": data.get("TMP", 0),
                    "humidity": data.get("REH", 0),
                    "wind_speed": data.get("WSD", 0),
                    "uv_index": 0.0,  # 별도 API 필요
                    "weather_condition": data.get("PTY", "맑음"),
                }
            )
        except Exception as e:
            print(f"[예보 저장 오류] {fcst_time}: {e}")
