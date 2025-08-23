import logging
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.utils import timezone

from ..models import WeatherCurrentInfo, WeatherFutureInfo
from ..utils.grid_converter import convert_to_grid

import ssl
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)

# 🔐 TLS Adapter 정의
class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        import urllib3
        ctx = ssl.create_default_context()
        ctx.set_ciphers('HIGH:!DH:!aNULL')
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('HIGH:!DH:!aNULL')
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        kwargs['ssl_context'] = ctx
        return super().proxy_manager_for(*args, **kwargs)

# 적용
session = requests.Session()
session.mount("https://", TLSAdapter())

# ----------------------------
# API 엔드포인트 상수
# ----------------------------
ULTRA_SRT_FCST_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
VILAGE_FCST_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

# ----------------------------
# 코드 매핑
# ----------------------------
PTY_CODE = {
    "0": "강수 없음",
    "1": "비",
    "2": "비/눈",
    "3": "눈",
    "5": "빗방울",
    "6": "진눈깨비",
    "7": "눈날림"
}
SKY_CODE = {"1": "맑음", "3": "구름많음", "4": "흐림"}
DEG_CODE = {
    0: "N", 22.5: "NNE", 45: "NE", 67.5: "ENE", 90: "E",
    112.5: "ESE", 135: "SE", 157.5: "SSE", 180: "S",
    202.5: "SSW", 225: "SW", 247.5: "WSW", 270: "W",
    292.5: "WNW", 315: "NW", 337.5: "NNW", 360: "N"
}

def deg_to_dir(deg):
    deg = deg % 360
    closest = min(DEG_CODE.keys(), key=lambda x: abs(x - deg))
    return DEG_CODE[closest]

# ----------------------------
# 안전한 Decimal 변환 함수
# ----------------------------
def safe_decimal(value):
    try:
        if value is None:
            return None
        return Decimal(str(round(float(value), 2)))
    except (ValueError, TypeError, InvalidOperation):
        return None

# ----------------------------
# 발표 시각 계산
# ----------------------------
def get_latest_base_time_for_ultra():
    now = timezone.localtime() - timedelta(hours=4)
    base_time = f"{now.hour:02}00"
    base_date = now.strftime("%Y%m%d")
    return base_date, base_time

def get_latest_base_time_for_vilage():
    now = timezone.localtime() - timedelta(hours=2)
    base_times = [2, 5, 8, 11, 14, 17, 20, 23]
    hour = now.hour
    base_hour = max([t for t in base_times if t <= hour], default=23)
    base_date = now.strftime("%Y%m%d")
    if hour < 2:
        base_date = (now - timedelta(days=1)).strftime("%Y%m%d")
        base_hour = 23
    return base_date, f"{base_hour:02}00"

# ----------------------------
# 초단기예보 호출 (JSON 응답)
# ----------------------------
def fetch_current_weather(lat, lon, location_name="사용자 위치"):
    nx, ny = convert_to_grid(lat, lon)
    base_date, base_time = get_latest_base_time_for_ultra()
    service_key = settings.KMA_API_KEY

    params = {
        "serviceKey": service_key,
        "dataType": "JSON",  # JSON 요청
        "numOfRows": "60",
        "pageNo": "1",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = session.get(ULTRA_SRT_FCST_URL, params=params, headers=headers, timeout=10, verify=True)
        response.raise_for_status()
        data = response.json()
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
    except Exception as e:
        logger.error(f"[기상청 초단기예보 오류] {e}")
        return False

    now = timezone.localtime()
    target_data = {}
    target_time = None

    for item in items:
        fcst_date = item.get("fcstDate")
        fcst_time = item.get("fcstTime")
        category = item.get("category")
        value = item.get("fcstValue")

        if not (fcst_date and fcst_time and category and value):
            continue

        fcst_datetime_naive = datetime.strptime(fcst_date + fcst_time, "%Y%m%d%H%M")
        fcst_datetime = timezone.make_aware(fcst_datetime_naive, timezone.get_current_timezone())
        
        if abs((fcst_datetime - now).total_seconds()) <= 3600:
            target_time = fcst_datetime
            target_data[category] = value

    if not target_time or not target_data:
        logger.warning("[기상청] 현재 시각에 해당하는 초단기예보 데이터 없음")
        return False

    WeatherCurrentInfo.objects.update_or_create(
        location_name=location_name,
        defaults={
            "latitude": safe_decimal(lat),
            "longitude": safe_decimal(lon),
            "temperature": safe_decimal(target_data.get("T1H")),
            "humidity": safe_decimal(target_data.get("REH")),
            "wind_speed": safe_decimal(target_data.get("WSD")),
            "uv_index": safe_decimal(target_data.get("UV")),
            "weather_condition": PTY_CODE.get(target_data.get("PTY", "0"), "강수 없음"),
        }
    )
    return True

# ----------------------------
# 단기예보 호출 (JSON 응답)
# ----------------------------
def fetch_forecast_weather(lat, lon, location_name="사용자 위치"):
    nx, ny = convert_to_grid(lat, lon)
    base_date, base_time = get_latest_base_time_for_vilage()
    service_key = settings.KMA_API_KEY

    params = {
        "serviceKey": service_key,
        "dataType": "JSON",  # JSON 요청
        "numOfRows": "1000",
        "pageNo": "1",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = session.get(VILAGE_FCST_URL, params=params, headers=headers, timeout=10, verify=True)
        response.raise_for_status()
        data = response.json()
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
    except Exception as e:
        logger.error(f"[기상청 단기예보 오류] {e}")
        return False

    forecast_data = {}
    for item in items:
        fcst_date = item.get("fcstDate")
        fcst_time = item.get("fcstTime")
        category = item.get("category")
        value = item.get("fcstValue")

        if not (fcst_date and fcst_time and category):
            continue

        key = f"{fcst_date}_{fcst_time}"
        forecast_data.setdefault(key, {})[category] = value

    if not forecast_data:
        logger.warning("[기상청] 단기예보 데이터 없음")
        return False

    for key, values in forecast_data.items():
        fcst_date, fcst_time = key.split("_")
        fcst_datetime = datetime.strptime(fcst_date + fcst_time, "%Y%m%d%H%M")

        WeatherFutureInfo.objects.update_or_create(
            location_name=location_name,
            time_set=fcst_datetime,
            defaults={
                "latitude": safe_decimal(lat),
                "longitude": safe_decimal(lon),
                "temperature": safe_decimal(values.get("TMP")),
                "humidity": safe_decimal(values.get("REH")),
                "wind_speed": safe_decimal(values.get("WSD")),
                "uv_index": safe_decimal(values.get("UV")),
                "weather_condition": PTY_CODE.get(values.get("PTY", "0"), "강수 없음"),
            }
        )
    return True

# ----------------------------
# 전체 업데이트
# ----------------------------
def update_weather_data():
    lat, lon = 37.5744, 127.0396  # 동대문구 좌표
    location_name = "동대문구"
    logger.info("[날씨 업데이트] 시작")

    success_current = fetch_current_weather(lat, lon, location_name)
    success_forecast = fetch_forecast_weather(lat, lon, location_name)

    if not success_current:
        logger.error("[날씨 업데이트] 초단기예보 업데이트 실패")
    if not success_forecast:
        logger.error("[날씨 업데이트] 단기예보 업데이트 실패")

    if success_current and success_forecast:
        logger.info("[날씨 업데이트] 완료")
    else:
        logger.warning("[날씨 업데이트] 일부 실패")


import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("urllib3").propagate = True