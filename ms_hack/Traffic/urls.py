from django.urls import path
from . import views

urlpatterns = [
    # LiveMapTraffic
    path('live_map_traffic/', views.LiveMapTrafficList.as_view()),
    path('live_map_traffic/<int:pk>/', views.LiveMapTrafficDetail.as_view()),

    # TrafficCurrentInfo
    path('traffic_current_info/', views.TrafficCurrentInfoList.as_view()),
    path('traffic_current_info/<int:pk>/', views.TrafficCurrentInfoDetail.as_view()),

    # TrafficFutureInfo
    path('traffic_future_info/', views.TrafficFutureInfoList.as_view()),
    path('traffic_future_info/<int:pk>/', views.TrafficFutureInfoDetail.as_view()),

    # 새로운 API: TMAP 데이터 가져오기 + 저장 + 예측
    path('update_traffic/', views.UpdateTrafficData.as_view()),
]
