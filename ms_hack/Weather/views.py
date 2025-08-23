from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from .models import UserDeviceToken, WeatherFutureInfo
from .serializers import WeatherFutureSerializer
from .services.weather_api import fetch_current_weather, fetch_forecast_weather
from .services.weather_alert import check_weather_alerts
from .services.shelter_alert import check_shelter_weather_risks
from .services.firebase import send_push_notification

class SaveFCMTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("fcm_token")
        if not token:
            token = self.generate_dummy_token(request.user)

        try:
            obj, created = UserDeviceToken.objects.update_or_create(
                user_id=request.user.id,
                defaults={"fcm_token": token}
            )
        except Exception as e:
            return Response({"error": f"DB 저장 실패: {str(e)}"}, status=500)

        status_code, result = send_push_notification(
            token=token,
            title="환영 메시지",
            body="FCM 토큰이 정상적으로 저장되었습니다."
        )

        return Response({
            "message": "FCM 토큰이 저장되었습니다.",
            "fcm_token": token,
            "created": created,
            "push_status": status_code,
            "push_result": result
        }, status=200)

    def generate_dummy_token(self, user):
        """ 테스트용 임시 토큰 생성 """
        return f"dummy_token_for_user_{user.id}"

class WeatherForecastView(generics.ListAPIView):
    serializer_class = WeatherFutureSerializer

    def get_queryset(self):
        location = self.request.query_params.get('location_name', '동대문구')
        return WeatherFutureInfo.objects.filter(location_name=location).order_by('time_set')

class CreateForecastWithOffsetView(generics.CreateAPIView):
    serializer_class = WeatherFutureSerializer
    queryset = WeatherFutureInfo.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            hour_offset = int(request.data.get("hour_offset", 0))
        except (ValueError, TypeError):
            return Response({"error": "hour_offset는 정수여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        time_set = timezone.now() + timedelta(hours=hour_offset)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(time_set=time_set)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class WeatherUpdateView(APIView):
    def post(self, request):
        try:
            lat = float(request.data.get("latitude", 37.5744))
            lon = float(request.data.get("longitude", 127.0396))
            location_name = request.data.get("location_name", "동대문구")

            current_result = fetch_current_weather(lat, lon, location_name)
            forecast_result = fetch_forecast_weather(lat, lon, location_name)

            if current_result is False and forecast_result is False:
                return Response({"error": "기상청 API 응답이 비어있거나 저장 실패"}, status=status.HTTP_204_NO_CONTENT)

            return Response({
                "message": "현재 및 예보 날씨 정보가 업데이트되었습니다.",
                "location": location_name,
                "latitude": lat,
                "longitude": lon
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserWeatherAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.user.id
            check_weather_alerts(user_id=user_id)
            return Response({"message": "사용자 기반 위험 분석 및 알림 완료"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShelterWeatherAlertView(APIView):
    def post(self, request):
        try:
            alerts = check_shelter_weather_risks()
            return Response({"alerts": alerts})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WeatherAlertTriggerView(APIView):
    def post(self, request):
        try:
            user_id = request.user.id
            check_weather_alerts(user_id=user_id)
            alerts = check_shelter_weather_risks()
            return Response({
                "message": "알림 트리거 완료",
                "user_alert": "사용자 위험 분석 완료",
                "shelter_alerts": alerts
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)