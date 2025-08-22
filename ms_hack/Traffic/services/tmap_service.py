# Traffic/services/tmap_service.py
import requests
from decouple import config

TMAP_APP_KEY = config('TMAP_APP_KEY').strip()

def fetch_realtime_traffic():
    """
    TMAP 실시간 교통 정보 호출 후, 모델/프론트 스펙에 맞게 정규화하여 반환
    """
    url = "https://apis.openapi.sk.com/tmap/traffic"
    headers = {
        "appKey": TMAP_APP_KEY,
        "Accept": "application/json"
    }
    params = {
        "version": 1,
        "minLat": 37.428,        # 서울 남서쪽
        "minLon": 126.764,
        "maxLat": 37.701,        # 서울 북동쪽
        "maxLon": 127.183,
        "centerLat": 37.565,     # 서울 중심
        "centerLon": 127.0,
        "reqCoordType": "WGS84GEO",
        "resCoordType": "WGS84GEO",
        "radius": 1,
        "zoomLevel": 10,         # 서울 전체가 한 화면에 나오도록 확대 수준 조정
        "sort": "index"
        }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        raw_data = response.json()

        features = []
        for item in raw_data.get('features', []):
            props = item.get('properties', {})
            geom = item.get('geometry', {})

            # 모델/프론트에 맞게 필드 이름 변환
            feature = {
                "traffic_id": props.get('id'),
                "name": props.get('name', ''),
                "startNodeName": props.get('startNodeName', 'unknown'),
                "endNodeName": props.get('endNodeName', 'unknown'),
                "congestion": props.get('congestion', 0),
                "speed": props.get('speed', 0),
                "distance": props.get('distance', 0),
                "direction": props.get('direction', 0),
                "roadType": props.get('roadType', ''),
                "coordinates": geom.get('coordinates', []),
                "updateTime": props.get('updateTime', ''),
                # 돌발 정보
                "isAccidentNode": props.get('isAccidentNode', 'N'),
                "accidentUpperCode": props.get('accidentUpperCode', ''),
                "description": props.get('description', '')
            }
            features.append(feature)

        return {"features": features}

    except requests.exceptions.HTTPError as e:
        print("HTTPError:", e.response.status_code, e.response.text)
        return None
    except Exception as e:
        print("Error:", e)
        return None
    
