import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from ..models import WeatherCurrentInfo, WeatherFutureInfo
from ..utils.grid_converter import convert_to_grid
from django.utils import timezone

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
    deg = deg % 360
    closest = min(DEG_CODE.keys(), key=lambda x: abs(x - deg))
    return DEG_CODE[closest]

# 발표 시각 계산
def get_latest_base_time_for_ultra():
    now = datetime.now()
    base_time = (now - timedelta(hours=1)).strftime("%H00")
    base_date = now.strftime("%Y%m%d")
    return base_date, base_time

def get_latest_base_time_for_vilage():
    now = datetime.now()
    base_times = [2, 5, 8, 11, 14, 17, 20, 23]
    hour = now.hour
    base_hour = max([t for t in base_times if t <= hour], default=23)
    base_date = now.strftime("%Y%m%d")
    if hour < 2:
        base_date = (now - timedelta(days=1)).strftime("%Y%m%d")
        base_hour = 23
    return base_date, f"{base_hour:02}00"

# ✅ 초단기예보
def fetch_current_weather(lat, lon, location_name="사용자 위치"):
    nx, ny = convert_to_grid(lat, lon)
    if ny == 127: ny = 126
    base_date, base_time = get_latest_base_time_for_ultra()

    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
    params = {
        "serviceKey": settings.KMA_API_KEY,
        "dataType": "JSON",
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
        response = requests.get(url, params=params, headers=headers, verify=True, timeout=10)
        response.raise_for_status()
        items = response.json()['response']['body']['items']['item']
    except Exception as e:
        logger.error(f"[기상청 초단기예보 오류] {e}")
        return False

    now = timezone.localtime()
    target_data = {}
    target_time = None

    for item in items:
        fcst_datetime = datetime.strptime(item['fcstDate'] + item['fcstTime'], "%Y%m%d%H%M")
        if abs((fcst_datetime - now).total_seconds()) <= 3600:
            target_time = fcst_datetime
            target_data[item['category']] = item['fcstValue']

    if not target_time or not target_data:
        logger.warning("[기상청] 현재 시각에 해당하는 예보 데이터 없음")
        return False

    WeatherCurrentInfo.objects.update_or_create(
        location_name=location_name,
        time_set=target_time,
        defaults={
            "latitude": lat,
            "longitude": lon,
            "temperature": float(target_data.get("T1H", 0)),
            "humidity": float(target_data.get("REH", 0)),
            "wind_speed": float(target_data.get("WSD", 0)),
            "uv_index": float(target_data.get("UV", 0.0)),
            "weather_condition": PTY_CODE.get(target_data.get("PTY", "0"), "맑음"),
        }
    )
    return True

# ✅ 단기예보
def fetch_forecast_weather(lat, lon, location_name="사용자 위치"):
    nx, ny = convert_to_grid(lat, lon)
    if ny == 127: ny = 126
    base_date, base_time = get_latest_base_time_for_vilage()

    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        "serviceKey": settings.KMA_API_KEY,
        "dataType": "JSON",
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
        response = requests.get(url, params=params, headers=headers, verify=True, timeout=10)
        response.raise_for_status()
        items = response.json()["response"]["body"]["items"]["item"]
    except Exception as e:
        logger.error(f"[기상청 단기예보 오류] {e}")
        return False

    forecast_data = {}
    for item in items:
        key = f"{item['fcstDate']}_{item['fcstTime']}"
        forecast_data.setdefault(key, {})[item["category"]] = item["fcstValue"]

    if not forecast_data:
        logger.warning("[기상청] 단기예보 데이터 없음")
        return False

    for key, values in forecast_data.items():
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
                "sky": SKY_CODE.get(values.get("SKY", "1")),
                "precipitation_type": PTY_CODE.get(values.get("PTY", "0")),
                "wind_speed": values.get("WSD"),
                "wind_direction": deg_to_dir(float(values.get("VEC", 0))),
                "rainfall": values.get("RN1"),
            }
        )

# ✅ 전체 업데이트 함수
def update_weather_data():
    lat, lon = 37.5744, 127.0396
    location_name = "동대문구"
    logger.info("[날씨 업데이트] 시작")
    current_result = fetch_current_weather(lat, lon, location_name)
    forecast_result = fetch_forecast_weather(lat, lon, location_name)
    logger.info("[날씨 업데이트] 완료")
