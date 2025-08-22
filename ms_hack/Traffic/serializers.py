from rest_framework import serializers
from .models import LiveMapTraffic, TrafficCurrentInfo, TrafficFutureInfo

# 1. LiveMapTraffic Serializer (실시간 데이터)
class LiveMapTrafficSerializer(serializers.ModelSerializer):
    traffic_id = serializers.ReadOnlyField()

    class Meta:
        model = LiveMapTraffic
        fields = [
            'traffic_id',
            'name',                 
            'startNodeName',        
            'endNodeName',          
            'congestion',           
            'speed',
            'distance',
            'direction',
            'roadType',
            'coordinates',
            'updateTime',
            'isAccidentNode',
            'accidentUpperCode',
            'description'
        ]


# 2. TrafficCurrentInfo Serializer
class TrafficCurrentInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='traffic.name', read_only=True)
    startNodeName = serializers.CharField(source='traffic.startNodeName', read_only=True)
    endNodeName = serializers.CharField(source='traffic.endNodeName', read_only=True)
    congestion = serializers.IntegerField(source='traffic.congestion', read_only=True)
    coordinate = serializers.ListField(read_only=True)  # 수정됨: source 제거, 모델 필드 그대로 사용

    # 돌발 정보
    isAccidentNode = serializers.CharField(read_only=True)
    accidentUpperCode = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)

    class Meta:
        model = TrafficCurrentInfo
        fields = [
            'traffic',
            'name',
            'startNodeName',
            'endNodeName',
            'congestion',
            'coordinate',       # livemap 좌표 그대로
            'updated_at',
            'isAccidentNode',
            'accidentUpperCode',
            'description'
        ]


# 3. TrafficFutureInfo Serializer
class TrafficFutureInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='traffic.name', read_only=True)
    original_congestion = serializers.IntegerField(source='traffic.congestion', read_only=True)
    
    class Meta:
        model = TrafficFutureInfo
        fields = [
            'traffic',
            'name',
            'original_congestion',
            'predicted_congestion',
            'time_set'
        ]
