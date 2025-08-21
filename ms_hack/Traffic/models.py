from django.db import models

# ==============================================
# LiveMapTraffic: 실시간 TMAP API 원본 데이터 저장
# ==============================================
class LiveMapTraffic(models.Model):
    traffic_id = models.AutoField(primary_key=True)
    road_name = models.CharField(max_length=100, default="unknown")   # 기존 row에도 기본값 적용
    start_node = models.CharField(max_length=100, default="unknown")  # startNodeName
    end_node = models.CharField(max_length=100, default="unknown")    # endNodeName
    congestion = models.IntegerField(default=0)                        # TMAP congestion (0~4)
    speed = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # km/h
    distance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # m
    direction = models.IntegerField(null=True, blank=True)             # 0:정방향, 1:역방향
    road_type = models.CharField(max_length=10, null=True, blank=True) # TMAP roadType
    coordinates = models.JSONField(default=list)                       # [[x1, y1], [x2, y2]] 형태
    update_time = models.DateTimeField(null=True, blank=True)          # 기존 row 없으면 null 허용              # TMAP updateTime

    class Meta:
        db_table = 'live_map_traffic'

    def __str__(self):
        return f"{self.road_name} ({self.start_node} → {self.end_node})"

# ==============================================
# TrafficCurrentInfo: 프론트용 현재 교통 정보
# ==============================================
class TrafficCurrentInfo(models.Model):
    traffic = models.OneToOneField(
        LiveMapTraffic, 
        on_delete=models.CASCADE,
        primary_key=True, 
        # null=True,       # 기존 row에 연결된 LiveMapTraffic이 없어도 허용
        # blank=True
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'traffic_current_info'

    def __str__(self):
        return f"{self.traffic.road_name} ({self.latitude}, {self.longitude})"

# ==============================================
# TrafficFutureInfo: 예측 교통 정보
# ==============================================
class TrafficFutureInfo(models.Model):
    traffic = models.OneToOneField(LiveMapTraffic, on_delete=models.CASCADE, primary_key=True)
    predicted_congestion = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    )
    time_set = models.DateTimeField()  # 예측 시점

    class Meta:
        db_table = 'traffic_future_info'

    def __str__(self):
        return f"{self.traffic.road_name} - {self.time_set} : {self.predicted_congestion}"
