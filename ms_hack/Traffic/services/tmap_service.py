# Traffic/services/tmap_service.py
'''import requests
from decouple import config
from datetime import datetime

TMAP_APP_KEY = config('TMAP_APP_KEY').strip()

def fetch_realtime_traffic():
    """
    TMAP 실시간 교통 정보 호출
    - 좌표 제한 없음
    """
    url = "https://apis.openapi.sk.com/tmap/traffic"
    headers = {
        "appKey": TMAP_APP_KEY,
        "Accept": "application/json"
    }
    params = {
    "version": 1,
    "reqCoordType": "WGS84GEO",
    "resCoordType": "WGS84GEO",
    "trafficType": "all",  # 필수
    "radius": 1,
    "zoomLevel": 1000,
    "sort": "index"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("HTTPError:", e.response.status_code, e.response.text)
        return None
    except Exception as e:
        print("Error:", e)
        return None
'''
import requests
from decouple import config

TMAP_APP_KEY = config('TMAP_APP_KEY').strip()

def fetch_realtime_traffic():
    """
    TMAP 실시간 교통 정보 호출
    """
    url = "https://apis.openapi.sk.com/tmap/traffic"
    headers = {
        "appKey": TMAP_APP_KEY,
        "Accept": "application/json"
    }
    params = {
        "version": 1,
        "minLat": 37.502183,
        "minLon": 126.951798,
        "maxLat": 37.542183,
        "maxLon": 126.991798,
        "centerLat": 37.522183,
        "centerLon": 126.971798,
        "reqCoordType": "WGS84GEO",
        "resCoordType": "WGS84GEO",
        "radius": 1,
        "zoomLevel": 7,
        "sort": "index"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        print("Request URL:", response.url)  # 디버그: 요청 URL 확인
        response.raise_for_status()          # HTTPError 발생 시 예외 처리
        data = response.json()
        print("Response received:", data)    # 디버그: 실제 응답 확인
        return data
    except requests.exceptions.HTTPError as e:
        print("HTTPError:", e.response.status_code, e.response.text)
        return None
    except Exception as e:
        print("Error:", e)
        return None
