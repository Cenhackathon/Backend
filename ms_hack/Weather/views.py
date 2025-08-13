from rest_framework.views import APIView
from rest_framework.response import Response
from .services.weather_api import fetch_weather_from_kma
from .services.weather_alert import check_weather_alerts
from .models import WeatherFutureInfo
from .serializers import WeatherFutureSerializer

class WeatherUpdateView(APIView):
    def post(self, request):
        try:
            fetch_weather_from_kma()
            return Response({"message": "날씨 정보가 업데이트되었습니다."})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class WeatherForecastView(APIView):
    def get(self, request):
        location = request.query_params.get('location_name', '동대문구')
        forecasts = WeatherFutureInfo.objects.filter(location_name=location).order_by('time_set')
        serializer = WeatherFutureSerializer(forecasts, many=True)
        return Response(serializer.data)

class WeatherAlertTriggerView(APIView):
    def post(self, request):
        try:
            check_weather_alerts()
            return Response({"message": "위험 요소 확인 및 알림 생성 완료"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
