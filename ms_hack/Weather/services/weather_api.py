import os
import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from ..models import WeatherCurrentInfo, WeatherFutureInfo
from ..utils.grid_converter import convert_to_grid  # 위도/경도 → 격자 변환

logger = logging.getLogger(__name__)

# 코드 매핑
PTY_CODE = {
    "0": "강수 없음", "1": "비", "2": "비/눈", "3": "눈",
    "5": "빗방울", "6": "진눈깨비", "7": "눈날림"
}
SKY_CODE = {
    "1": "맑음", "3": "구름많음", "4": "흐림"
}
DEG_CODE = {
    0: "N", 22.5: "NNE", 45: "NE", 67.5: "ENE", 90: "E",
    112.5: "ESE", 135: "SE", 157.5: "SSE", 180: "S",
    202.5: "SSW", 225: "SW", 247.5: "WSW", 270: "W",
    292.5: "WNW", 315: "NW", 337.5: "NNW", 360: "N"
}

def deg_to_dir(deg):
    closest = min(DEG_CODE.keys(), key=lambda x: abs(x - deg))
    return DEG_CODE[closest]

# ✅ 1. 현재 날씨 (초단기예보)
def fetch_current_weather(lat, lon, location_name="사용자 위치"):
    nx, ny = convert_to_grid(lat, lon)
    base_time = (datetime.now() - timedelta(hours=1)).strftime("%H00")
    base_date = datetime.now().strftime("%Y%m%d")

    params = {
        "serviceKey": os.getenv("KMA_API_KEY", settings.KMA_API_KEY),
        "numOfRows": "60",
        "pageNo": "1",
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny
    }

    try:
        response = requests.get(
            "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst",
            params=params, verify=False
        )
        response.raise_for_status()
        items = response.json()['response']['body']['items']['item']
    except Exception as e:
        logger.error(f"[기상청 초단기예보 오류] {e}")
        return

    now = datetime.now()
    target_time = None
    target_data = {}

    for item in items:
        fcst_datetime = datetime.strptime(item['fcstDate'] + item['fcstTime'], "%Y%m%d%H%M")
        if abs((fcst_datetime - now).total_seconds()) <= 3600:
            target_time = fcst_datetime
            target_data[item['category']] = item['fcstValue']

    if not target_time:
        logger.warning("[기상청] 현재 시각에 해당하는 예보 데이터 없음")
        return

    WeatherCurrentInfo.objects.update_or_create(
        location_name=location_name,
        time_set=target_time,
        defaults={
            "latitude": lat,
            "longitude": lon,
            "temperature": float(target_data.get("T1H", 0)),
            "humidity": float(target_data.get("REH", 0)),
            "wind_speed": float(target_data.get("WSD", 0)),
            "uv_index": 0.0,
            "weather_condition": PTY_CODE.get(target_data.get("PTY", "0"), "맑음"),
        }
    )

# ✅ 2. 미래 날씨 (단기예보)
def fetch_forecast_weather(lat, lon, location_name="사용자 위치"):
    nx, ny = convert_to_grid(lat, lon)
    base_date = datetime.now().strftime("%Y%m%d")
    base_time = "0500"

    params = {
        "serviceKey": os.getenv("KMA_API_KEY", settings.KMA_API_KEY),
        "numOfRows": "1000",
        "pageNo": "1",
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny,
    }

    try:
        response = requests.get(
            "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst",
            params=params
        )
        response.raise_for_status()
        items = response.json()["response"]["body"]["items"]["item"]
    except Exception as e:
        logger.error(f"[기상청 단기예보 오류] {e}")
        return

    parsed = {}
    for item in items:
        key = f"{item['fcstDate']}_{item['fcstTime']}"
        if key not in parsed:
            parsed[key] = {}
        parsed[key][item["category"]] = item["fcstValue"]

    for key, values in parsed.items():
        fcst_date, fcst_time = key.split("_")
        WeatherFutureInfo.objects.update_or_create(
            fcst_date=fcst_date,
            fcst_time=fcst_time,
            location_name=location_name,
            defaults={
                "latitude": lat,
                "longitude": lon,
                "temperature": values.get("TMP"),
                "humidity": values.get("REH"),
                "sky": values.get("SKY"),
                "precipitation_type": values.get("PTY"),
                "wind_speed": values.get("WSD"),
                "wind_direction": values.get("VEC"),
                "rainfall": values.get("RN1"),
            }
        )

