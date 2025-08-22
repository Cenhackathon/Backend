from django.utils import timezone
from datetime import timedelta
# Traffic/views.py

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import timedelta

from .models import LiveMapTraffic, TrafficCurrentInfo, TrafficFutureInfo
from .serializers import (
    LiveMapTrafficSerializer,
    TrafficCurrentInfoSerializer,
    TrafficFutureInfoSerializer
)
from .services.tmap_service import fetch_realtime_traffic
from .services.traffic_prediction import predict_congestion

# -------------------
# 1️⃣ LiveMapTraffic (읽기 전용)
class LiveMapTrafficList(generics.ListAPIView):
    queryset = LiveMapTraffic.objects.all()
    serializer_class = LiveMapTrafficSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        accident = self.request.query_params.get('isAccidentNode')
        if accident in ['Y', 'N']:
            queryset = queryset.filter(isAccidentNode=accident)
        return queryset

class LiveMapTrafficDetail(generics.RetrieveAPIView):
    queryset = LiveMapTraffic.objects.all()
    serializer_class = LiveMapTrafficSerializer
    permission_classes = [AllowAny]

# -------------------
# 2️⃣ TrafficCurrentInfo (읽기 전용)
class TrafficCurrentInfoList(generics.ListAPIView):
    queryset = TrafficCurrentInfo.objects.all()
    serializer_class = TrafficCurrentInfoSerializer
    permission_classes = [AllowAny]

    # def get_queryset(self):
    #     queryset = TrafficCurrentInfo.objects.all()
    #     accident = self.request.query_params.get('accident')
    #     if accident in ['Y', 'N']:
    #         queryset = queryset.filter(isAccidentNode=accident)
    #     return queryset

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
# 4️⃣ TMAP 데이터 가져오기 + 예측 + DB 저장
class UpdateTrafficData(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # 1️⃣ 최신 데이터 확인 (5분 내 업데이트 생략)
        five_minutes_ago = timezone.now() - timedelta(minutes=5)
        latest_current = TrafficCurrentInfo.objects.order_by('-updated_at').first()
        if latest_current and latest_current.updated_at > five_minutes_ago:
            return Response({
                "message": "최신 데이터 존재. API 호출 생략",
                "updated_at": latest_current.updated_at
            }, status=status.HTTP_200_OK)

        # 2️⃣ TMAP API 호출
        data = fetch_realtime_traffic()
        if not data or "features" not in data:
            return Response({"error": "TMAP API 호출 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        live_objs = []
        current_objs = []
        future_objs = []

        for item in data.get('features', []):
            props = item.get('properties', {})
            geom = item.get('geometry', {})

            # 4️⃣ TrafficCurrentInfo 저장 (coordinate 중심) # 수정됨
            current_coordinate = live_obj.coordinates  # [[lon, lat], [lon, lat], ...]
            if current_coordinate and isinstance(current_coordinate[0], list):
                coordinate = current_coordinate[0]  # 첫 번째 좌표만 사용
            else:
                coordinate = [0.0, 0.0]

            current_obj, _ = TrafficCurrentInfo.objects.update_or_create(
                traffic=live_obj,
                defaults={
                    "coordinate": coordinate,
                    "name": props.get('name', ''),
                    "updated_at": timezone.now(),
                    "congestion": props.get('congestion', 0),
                    "isAccidentNode": props.get('isAccidentNode', 'N'),
                    "accidentUpperCode": props.get('accidentUpperCode', ''),
                    "description": props.get('description', '')
                }
            )

            current_objs.append(current_obj)


            # 4️⃣ TrafficCurrentInfo 저장 (coordinate 중심) # 수정됨
            coordinate = geom.get('coordinates', [])
            if coordinate and isinstance(coordinate[0], list):
                # 다차원 배열일 경우, 첫 번째 좌표 사용
                coordinate = coordinate[0]
            else:
                coordinate = [0.0, 0.0]

            current_obj, _ = TrafficCurrentInfo.objects.update_or_create(
                traffic=live_obj,
                defaults={
                    "coordinate": coordinate,                 # 수정됨: latitude/longitude 제거, coordinate 사용
                    "name": props.get('name', ''),
                    "updated_at": timezone.now(),
                    "congestion": props.get('congestion', 0),
                    "isAccidentNode": props.get('isAccidentNode', 'N'),
                    "accidentUpperCode": props.get('accidentUpperCode', ''),
                    "description": props.get('description', '')
                }
            )
            current_objs.append(current_obj)

            # 5️⃣ TrafficFutureInfo 저장 (예측)
            predicted_level = predict_congestion(live_obj.name, live_obj.congestion)
            future_obj, _ = TrafficFutureInfo.objects.update_or_create(
                traffic=live_obj,
                defaults={
                    "predicted_congestion": predicted_level,
                    "time_set": timezone.now()
                }
            )
            future_objs.append(future_obj)

        # 6️⃣ Serializer로 결과 반환
        current_data = TrafficCurrentInfoSerializer(current_objs, many=True).data
        future_data = TrafficFutureInfoSerializer(future_objs, many=True).data

        return Response({
            "current_count": len(current_objs),
            "future_count": len(future_objs),
            "current_data": current_data,
            "future_data": future_data
        }, status=status.HTTP_200_OK)
