# Traffic/services/tmap_service.py
import requests
from decouple import config

TMAP_APP_KEY = config('TMAP_APP_KEY')

def fetch_tmap_data(keyword="SKT"):
    """
    TMAP API 호출하여 POI 데이터를 가져오는 함수
    """
    url = "https://apis.openapi.sk.com/tmap/pois"
    headers = {
        "appKey": TMAP_APP_KEY,
        "Accept": "application/json"
    }
    params = {
        "version": 1,
        "searchKeyword": keyword,
        "searchType": "all",
        "page": 1,
        "count": 20,
        "resCoordType": "WGS84GEO",
        "multiPoint": "N",
        "searchtypCd": "A",
        "reqCoordType": "WGS84GEO",
        "poiGroupYn": "N"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None
