# Traffic/serializers.py

from rest_framework import serializers
from .models import Live_Map_Traffic, Traffic_Current_Info, Traffic_Future_Info

# 1. Live_Map_Traffic Serializer
class LiveMapTrafficSerializer(serializers.ModelSerializer):
    class Meta:
        model = Live_Map_Traffic
        fields = '__all__'

# 2. Traffic_Current_Info Serializer
class TrafficCurrentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traffic_Current_Info
        fields = '__all__'

# 3. Traffic_Future_Info Serializer
class TrafficFutureInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traffic_Future_Info
        fields = '__all__'
