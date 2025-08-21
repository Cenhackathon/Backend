# Traffic/serializers.py

from rest_framework import serializers
from .models import LiveMapTraffic, TrafficCurrentInfo, TrafficFutureInfo

# 1. LiveMapTraffic Serializer (실시간 데이터)
class LiveMapTrafficSerializer(serializers.ModelSerializer):
    traffic_id = serializers.ReadOnlyField()

    class Meta:
        model = LiveMapTraffic
        fields = ['traffic_id', 'road_name', 'congestion']


# TrafficCurrentInfo: FK 연결된 traffic 정보 포함
class TrafficCurrentInfoSerializer(serializers.ModelSerializer):
    road_name = serializers.CharField(source='traffic.road_name', read_only=True)
    congestion = serializers.IntegerField(source='traffic.congestion', read_only=True)

    class Meta:
        model = TrafficCurrentInfo
        fields = ['traffic', 'road_name', 'congestion', 'latitude', 'longitude', 'updated_at']

# TrafficFutureInfo: FK 연결된 traffic 정보 포함
class TrafficFutureInfoSerializer(serializers.ModelSerializer):
    road_name = serializers.CharField(source='traffic.road_name', read_only=True)
    original_congestion = serializers.IntegerField(source='traffic.congestion', read_only=True)

    class Meta:
        model = TrafficFutureInfo
        fields = ['traffic', 'road_name', 'original_congestion', 'predicted_congestion', 'time_set']