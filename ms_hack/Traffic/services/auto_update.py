from django.utils import timezone  # timezone-aware
import time
import threading
from datetime import timedelta
from Traffic.services.tmap_service import fetch_realtime_traffic
from Traffic.services.traffic_prediction import predict_congestion
from Traffic.models import LiveMapTraffic, TrafficCurrentInfo, TrafficFutureInfo

def update_traffic_data():
    latest = TrafficCurrentInfo.objects.order_by('-updated_at').first()
    if latest and (timezone.now() - latest.updated_at) < timedelta(minutes=5):
        print("최신 데이터 존재, API 호출 생략")
        return

    data = fetch_realtime_traffic()
    if not data:
        print("TMAP API 호출 실패")
        return

    live_objs = []
    for item in data.get('features', []):  # TMAP 새 엔드포인트 기준
        properties = item.get('properties', {})
        geometry = item.get('geometry', {})
        live_obj, _ = LiveMapTraffic.objects.update_or_create(
            traffic_id=properties.get('id'),
            defaults={
                "road_name": properties.get('name', ''),
                "start_node": properties.get('startNodeName', 'unknown'),
                "end_node": properties.get('endNodeName', 'unknown'),
                "congestion": properties.get('congestion', 0),
                "speed": properties.get('speed', 0),
                "distance": properties.get('distance', 0),
                "direction": properties.get('direction', 0),
                "road_type": properties.get('roadType', ''),
                "coordinates": geometry.get('coordinates', []),
                "update_time": timezone.now()
            }
        )
        live_objs.append(live_obj)

    current_list = []
    for obj in live_objs:
        current_obj, _ = TrafficCurrentInfo.objects.update_or_create(
            traffic=obj,
            defaults={
                "latitude": obj.latitude,
                "longitude": obj.longitude,
                "updated_at": timezone.now()
            }
        )
        current_list.append(current_obj)

    for obj in current_list:
        predicted_level = predict_congestion(obj.traffic.road_name, obj.traffic.congestion)
        TrafficFutureInfo.objects.update_or_create(
            traffic=obj.traffic,
            defaults={
                "predicted_congestion": predicted_level,
                "time_set": timezone.now()
            }
        )

    print(f"업데이트 완료: {len(current_list)}개 current, {len(live_objs)}개 live")


def start_auto_update():
    """서버 시작 시 5분마다 자동 실행"""
    def run():
        while True:
            try:
                update_traffic_data()
            except Exception as e:
                print("자동 업데이트 중 오류:", e)
            time.sleep(300)  # 5분마다 실행

    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()
