from django.urls import path
from . import views

urlpatterns = [
    # 1️⃣ LiveMapTraffic (읽기 전용)
    path('live_map_traffic/', views.LiveMapTrafficList.as_view(), name='live_map_traffic_list'),
    path('live_map_traffic/<int:pk>/', views.LiveMapTrafficDetail.as_view(), name='live_map_traffic_detail'),

    # 2️⃣ TrafficCurrentInfo (읽기 전용)
    path('traffic_current_info/', views.TrafficCurrentInfoList.as_view(), name='traffic_current_info_list'),
    path('traffic_current_info/<int:pk>/', views.TrafficCurrentInfoDetail.as_view(), name='traffic_current_info_detail'),

    # 3️⃣ TrafficFutureInfo (읽기 전용)
    path('traffic_future_info/', views.TrafficFutureInfoList.as_view(), name='traffic_future_info_list'),
    path('traffic_future_info/<int:pk>/', views.TrafficFutureInfoDetail.as_view(), name='traffic_future_info_detail'),

    # 4️⃣ TMAP 데이터 가져오기 + 예측 + 저장
    path('update_traffic/', views.UpdateTrafficData.as_view(), name='update_traffic'),
]
