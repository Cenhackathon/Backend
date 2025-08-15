<<<<<<< HEAD
from rest_framework import generics
=======
from rest_framework import generics, status
>>>>>>> a612fed5123bf242e48ed7ca2929411a2348ddb2
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
<<<<<<< HEAD
from .models import WeatherFutureInfo, WeatherCurrentInfo
from .serializers import WeatherFutureSerializer, WeatherCurrentSerializer
from .services.weather_api import fetch_weather_from_kma
from .services.weather_alert import check_weather_alerts


class WeatherUpdateView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
=======

from .models import WeatherFutureInfo
from .serializers import WeatherFutureSerializer
from .services.weather_api import fetch_weather_from_kma
from .services.weather_alert import check_weather_alerts

# 1. 날씨 예보 리스트 조회 (GET)
class WeatherForecastView(generics.ListAPIView):
    serializer_class = WeatherFutureSerializer

    def get_queryset(self):
        location = self.request.query_params.get('location_name', '동대문구')
        return WeatherFutureInfo.objects.filter(location_name=location).order_by('time_set')

# 2. 시간 오프셋 기반 예보 생성 (POST)
class CreateForecastWithOffsetView(generics.CreateAPIView):
    serializer_class = WeatherFutureSerializer
    queryset = WeatherFutureInfo.objects.all()

    def perform_create(self, serializer):
        hour_offset = int(self.request.data.get("hour_offset", 0))
        time_set = datetime.now() + timedelta(hours=hour_offset)
        serializer.save(time_set=time_set)

# 3. 날씨 정보 업데이트 (기상청 API 호출) — 커스텀 로직이므로 APIView 유지
class WeatherUpdateView(APIView):
    def post(self, request):
>>>>>>> a612fed5123bf242e48ed7ca2929411a2348ddb2
        try:
            fetch_weather_from_kma()
            return Response({"message": "날씨 정보가 업데이트되었습니다."})
        except Exception as e:
<<<<<<< HEAD
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
=======
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 4. 위험 요소 확인 및 알림 생성 — 커스텀 로직이므로 APIView 유지
class WeatherAlertTriggerView(APIView):
    def post(self, request):
>>>>>>> a612fed5123bf242e48ed7ca2929411a2348ddb2
        try:
            check_weather_alerts()
            return Response({"message": "위험 요소 확인 및 알림 생성 완료"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

<<<<<<< HEAD

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
=======
# 5. shelter 데이터 경보 호출
from Weather.services.shelter_alert import check_shelter_weather_risks

class WeatherAlertTriggerView(APIView):
    def post(self, request):
        try:
            alerts = check_shelter_weather_risks()
            return Response({"alerts": alerts})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
>>>>>>> a612fed5123bf242e48ed7ca2929411a2348ddb2
