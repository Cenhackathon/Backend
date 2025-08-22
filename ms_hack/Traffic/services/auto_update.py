from django.utils import timezone
import time
import threading
from datetime import timedelta
from Traffic.services.tmap_service import fetch_realtime_traffic
from Traffic.services.traffic_prediction import predict_congestion
from Traffic.models import LiveMapTraffic, TrafficCurrentInfo, TrafficFutureInfo

def update_traffic_data():
    # 1️⃣ 5분 이내 최신 데이터 확인
    latest = TrafficCurrentInfo.objects.order_by('-updated_at').first()
    if latest and (timezone.now() - latest.updated_at) < timedelta(minutes=5):
        print("최신 데이터 존재, API 호출 생략")
        return

    # 2️⃣ TMAP API 호출
    data = fetch_realtime_traffic()
    if not data:
        print("TMAP API 호출 실패")
        return

    # 3️⃣ LiveMapTraffic 저장
    live_objs = []
    for item in data.get('features', []):
        props = item
        live_obj, _ = LiveMapTraffic.objects.update_or_create(
            traffic_id=props.get('traffic_id'),
            defaults={
                "name": props.get('name', ''),
                "startNodeName": props.get('startNodeName', 'unknown'),
                "endNodeName": props.get('endNodeName', 'unknown'),
                "congestion": props.get('congestion', 0),
                "speed": props.get('speed', 0),
                "distance": props.get('distance', 0),
                "direction": props.get('direction', 0),
                "roadType": props.get('roadType', ''),
                "coordinates": props.get('coordinates', []),
                "updateTime": timezone.now(),
                # 사고 관련 필드 추가
                "isAccidentNode": props.get('isAccidentNode', 'N'),
                "accidentUpperCode": props.get('accidentUpperCode', ''),
                "accidentUpperName": props.get('accidentUpperName', ''),
                "accidentDetailCode": props.get('accidentDetailCode', ''),
                "accidentDetailName": props.get('accidentDetailName', ''),
                "description": props.get('description', '')
            }
        )
        live_objs.append(live_obj)

    # 4️⃣ TrafficCurrentInfo 저장
    current_list = []
    for obj, item in zip(live_objs, data.get('features', [])):
        current_obj, _ = TrafficCurrentInfo.objects.update_or_create(
            traffic=obj,
            defaults={
                "coordinate": item.get('coordinates', []),  
                "updated_at": timezone.now(),
                "isAccidentNode": item.get('isAccidentNode', 'N'),
                "accidentUpperCode": item.get('accidentUpperCode', ''),
                "description": item.get('description', '')
            }
        )
        current_list.append(current_obj)

    # 5️⃣ TrafficFutureInfo 저장 (예측)
    for obj in current_list:
        predicted_level = predict_congestion(obj.traffic.name, obj.traffic.congestion)
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