from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
from .models import WeatherFutureInfo
from .serializers import WeatherFutureSerializer
from .services.weather_api import fetch_current_weather, fetch_forecast_weather
from .services.weather_alert import check_weather_alerts
from .services.shelter_alert import check_shelter_weather_risks

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

# 3. 날씨 정보 업데이트 (기상청 API 호출)
from .services.weather_api import fetch_current_weather, fetch_forecast_weather

class WeatherUpdateView(APIView):
    def post(self, request):
        try:
            lat = float(request.data.get("latitude", 37.5744))
            lon = float(request.data.get("longitude", 127.0396))
            location_name = request.data.get("location_name", "동대문구")

            # 현재 날씨 저장
            fetch_current_weather(lat, lon, location_name)

            # 미래 예보 저장
            fetch_forecast_weather(lat, lon, location_name)

            return Response({"message": "현재 및 예보 날씨 정보가 업데이트되었습니다."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 4. 사용자 기반 위험 요소 확인 및 FCM 알림 전송
class UserWeatherAlertView(APIView):
    def post(self, request):
        try:
            user_id = request.user.id  # 로그인된 사용자 ID
            check_weather_alerts(user_id=user_id)
            return Response({"message": "사용자 기반 위험 분석 및 알림 완료"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 5. 쉼터 기반 위험 요소 분석 결과 반환
class ShelterWeatherAlertView(APIView):
    def post(self, request):
        try:
            alerts = check_shelter_weather_risks()
            return Response({"alerts": alerts})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)