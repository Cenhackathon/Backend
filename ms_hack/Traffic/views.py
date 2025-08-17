from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .models import LiveMapTraffic, TrafficCurrentInfo, TrafficFutureInfo
from .serializers import (
    LiveMapTrafficSerializer,
    TrafficCurrentInfoSerializer,
    TrafficFutureInfoSerializer
)
from .services.tmap_service import fetch_tmap_data
from .services.traffic_prediction import predict_congestion
from datetime import datetime


# LiveMapTraffic
class LiveMapTrafficList(generics.ListCreateAPIView):
    queryset = LiveMapTraffic.objects.all()
    serializer_class = LiveMapTrafficSerializer

class LiveMapTrafficDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = LiveMapTraffic.objects.all()
    serializer_class = LiveMapTrafficSerializer

# TrafficCurrentInfo
class TrafficCurrentInfoList(generics.ListCreateAPIView):
    queryset = TrafficCurrentInfo.objects.all()
    serializer_class = TrafficCurrentInfoSerializer

class TrafficCurrentInfoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrafficCurrentInfo.objects.all()
    serializer_class = TrafficCurrentInfoSerializer

# TrafficFutureInfo
class TrafficFutureInfoList(generics.ListCreateAPIView):
    queryset = TrafficFutureInfo.objects.all()
    serializer_class = TrafficFutureInfoSerializer

class TrafficFutureInfoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrafficFutureInfo.objects.all()
    serializer_class = TrafficFutureInfoSerializer


# -------------------
from rest_framework.views import APIView

class UpdateTrafficData(APIView):
    """
    TMAP API 호출하여 현재 트래픽 데이터 저장,
    예측 후 TrafficFutureInfo에 저장
    """
    def get(self, request):
        # 1. TMAP API 호출
        data = fetch_tmap_data(keyword="강남대로")  # 예시: 특정 키워드
        if not data:
            return Response({"error": "TMAP API 호출 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 2. 현재 정보 DB 저장
        current_list = []
        for item in data.get('searchPoiInfo', {}).get('pois', []):
            current_obj, created = TrafficCurrentInfo.objects.update_or_create(
                traffic_id=item['id'],  # TMAP API에서 unique id 사용
                defaults={
                    "road_name": item.get('name', ''),
                    "congestion_level": "low",  # API에 혼잡도 없으면 기본값
                    "latitude": float(item.get('noorLat', 0)),
                    "longitude": float(item.get('noorLon', 0)),
                    "updated_at": datetime.now()
                }
            )
            current_list.append(current_obj)
        
        # 3. 예측 및 FutureInfo DB 저장
        future_list = []
        for obj in current_list:
            predicted_level = predict_congestion(obj.road_name, obj.congestion_level)
            future_obj = TrafficFutureInfo.objects.update_or_create(
                traffic_id=obj.traffic_id,
                defaults={
                    "road_name": obj.road_name,
                    "congestion_level": predicted_level,
                    "source_id": 1,  # 예시: 고정값
                    "time_set": datetime.now()
                }
            )
            future_list.append(future_obj)
        
        return Response({
            "current_count": len(current_list),
            "future_count": len(future_list)
        }, status=status.HTTP_200_OK)