from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
from .models import WeatherFutureInfo, WeatherCurrentInfo
from .serializers import WeatherFutureSerializer, WeatherCurrentSerializer
from .services.weather_api import fetch_weather_from_kma
from .services.weather_alert import check_weather_alerts
from .services.shelter_alert import check_shelter_weather_risks


class WeatherUpdateView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            fetch_weather_from_kma()
            return Response({"message": "날씨 정보가 업데이트되었습니다."})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# 미래 날씨 예보 조회 (GET) → ListAPIView 활용 가능
class WeatherForecastView(generics.ListAPIView):
    serializer_class = WeatherFutureSerializer

    def get_queryset(self):
        location = self.request.query_params.get('location_name', '동대문구')
        return WeatherFutureInfo.objects.filter(location_name=location).order_by('time_set')


# 위험 요소 확인 및 알림 생성 (POST)
class WeatherAlertTriggerView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            check_weather_alerts()
            return Response({"message": "사용자 기반 위험 분석 및 알림 완료"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 오프셋 기준 예보 생성 (POST)
class CreateForecastWithOffsetView(generics.CreateAPIView):
    serializer_class = WeatherFutureSerializer

    def create(self, request, *args, **kwargs):
        try:
            hour_offset = int(request.data.get("hour_offset", 0))
            time_set = datetime.now() + timedelta(hours=hour_offset)

            instance = WeatherFutureInfo.objects.create(
                location_name=request.data.get("location_name"),
                latitude=request.data.get("latitude"),
                longitude=request.data.get("longitude"),
                temperature=request.data.get("temperature"),
                humidity=request.data.get("humidity"),
                wind_speed=request.data.get("wind_speed"),
                uv_index=request.data.get("uv_index"),
                weather_condition=request.data.get("weather_condition"),
                time_set=time_set
            )
            serializer = self.get_serializer(instance)
            return Response({
                "message": f"{hour_offset}시간 뒤 예보가 저장되었습니다.",
                "data": serializer.data
            })
        except Exception as e:
            return Response({"error": str(e)}, status=400)
