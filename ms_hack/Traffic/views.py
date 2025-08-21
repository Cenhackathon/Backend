
# Traffic/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
from .models import LiveMapTraffic, TrafficCurrentInfo, TrafficFutureInfo
from .serializers import (
    LiveMapTrafficSerializer,
    TrafficCurrentInfoSerializer,
    TrafficFutureInfoSerializer
)
from .services.tmap_service import fetch_realtime_traffic
from .services.traffic_prediction import predict_congestion
from rest_framework.permissions import AllowAny

# -------------------
# 1️⃣ LiveMapTraffic (읽기 전용)
class LiveMapTrafficList(generics.ListAPIView):
    queryset = LiveMapTraffic.objects.all()
    serializer_class = LiveMapTrafficSerializer
    permission_classes = [AllowAny]

class LiveMapTrafficDetail(generics.RetrieveAPIView):
    queryset = LiveMapTraffic.objects.all()
    serializer_class = LiveMapTrafficSerializer

# -------------------
# 2️⃣ TrafficCurrentInfo (읽기 전용)
class TrafficCurrentInfoList(generics.ListAPIView):
    queryset = TrafficCurrentInfo.objects.all()
    serializer_class = TrafficCurrentInfoSerializer
    permission_classes = [AllowAny]

class TrafficCurrentInfoDetail(generics.RetrieveAPIView):
    queryset = TrafficCurrentInfo.objects.all()
    serializer_class = TrafficCurrentInfoSerializer
    permission_classes = [AllowAny]

# -------------------
# 3️⃣ TrafficFutureInfo (읽기 전용)
class TrafficFutureInfoList(generics.ListAPIView):
    queryset = TrafficFutureInfo.objects.all()
    serializer_class = TrafficFutureInfoSerializer
    permission_classes = [AllowAny]

class TrafficFutureInfoDetail(generics.RetrieveAPIView):
    queryset = TrafficFutureInfo.objects.all()
    serializer_class = TrafficFutureInfoSerializer
    permission_classes = [AllowAny]

# -------------------
# # 4️⃣ TMAP 데이터 가져오기 + 예측 + DB 저장
class UpdateTrafficData(APIView):
    permission_classes = [AllowAny]
    """
    TMAP API 호출하여 현재 트래픽 데이터 저장,
    예측 후 TrafficFutureInfo에 저장
    """
    def post(self, request):
        # 1️⃣ 최신 데이터 확인 (5분 내에 DB에 있으면 생략)
        five_minutes_ago = timezone.now() - timedelta(minutes=5)
        latest_current = TrafficCurrentInfo.objects.order_by('-updated_at').first()
        if latest_current and latest_current.updated_at > five_minutes_ago:
            return Response({
                "message": "최신 데이터 존재. API 호출 생략",
                "updated_at": latest_current.updated_at
            }, status=status.HTTP_200_OK)

        # 2️⃣ TMAP API 호출
        data = fetch_realtime_traffic()
        if not data:
            return Response({"error": "TMAP API 호출 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3️⃣ LiveMapTraffic 저장
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

        # 4️⃣ TrafficCurrentInfo 저장
        current_list = []
        for obj in live_objs:
            current_obj, _ = TrafficCurrentInfo.objects.update_or_create(
                traffic=obj,
                defaults={
                    "latitude": 0,
                    "longitude": 0,
                    "updated_at": timezone.now()
                }
            )
            current_list.append(current_obj)

        # 5️⃣ TrafficFutureInfo 저장 (예측)
        future_list = []
        for obj in current_list:
            predicted_level = predict_congestion(obj.traffic.road_name, obj.traffic.congestion)
            future_obj, _ = TrafficFutureInfo.objects.update_or_create(
                traffic=obj.traffic,
                defaults={
                    "predicted_congestion": predicted_level,
                    "time_set": timezone.now()
                }
            )
            future_list.append(future_obj)

        # 6️⃣ Serializer로 결과 반환
        future_data = TrafficFutureInfoSerializer(future_list, many=True).data

        return Response({
            "current_count": len(current_list),
            "future_count": len(future_list),
            "future_data": future_data
        }, status=status.HTTP_200_OK)