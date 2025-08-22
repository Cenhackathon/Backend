from django.db import models

# ==============================================
# LiveMapTraffic: 실시간 TMAP API 원본 데이터 저장 (히스토리 로그)
# ==============================================
class LiveMapTraffic(models.Model):
    traffic_id = models.AutoField(primary_key=True)

    # TMAP 필드명 기준
    name = models.CharField(max_length=100, default="unknown")               # 도로명
    startNodeName = models.CharField(max_length=100, default="unknown")      # 시작 노드명
    endNodeName = models.CharField(max_length=100, default="unknown")        # 종료 노드명

    congestion = models.IntegerField(                                        # 혼잡도 0~4
        choices=[
            (0, '정보없음'),
            (1, '원활'),
            (2, '서행'),
            (3, '지체'),
            (4, '정체'),
        ],
        default=0
    )
    speed = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)   # km/h
    distance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0) # m
    direction = models.IntegerField(null=True, blank=True)                     # 0: 정방향, 1: 역방향
    roadType = models.CharField(max_length=10, null=True, blank=True)         # TMAP roadType
    coordinates = models.JSONField(default=list)                               # [[lon, lat], [lon, lat]] 형태
    updateTime = models.DateTimeField(null=True, blank=True)                   # 교통정보 최종 업데이트

    # 사고 관련
    isAccidentNode = models.CharField(max_length=1, choices=[('Y','Yes'),('N','No')], default='N')
    accidentUpperCode = models.CharField(max_length=5, null=True, blank=True)
    accidentUpperName = models.CharField(max_length=50, null=True, blank=True)
    accidentDetailCode = models.CharField(max_length=5, null=True, blank=True)
    accidentDetailName = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)                      # 소통정보 / 사고 상세

    class Meta:
        db_table = 'live_map_traffic'

    def __str__(self):
        return f"{self.name} ({self.startNodeName} → {self.endNodeName})"


# ==============================================
#  TrafficCurrentInfo: 프론트용 현재 교통 정보 캐시
# ==============================================
class TrafficCurrentInfo(models.Model):
    traffic = models.OneToOneField(
        LiveMapTraffic,
        on_delete=models.CASCADE,
        primary_key=True
    )

    # 위치 정보: [경도, 위도] 배열로 저장
    coordinate = models.JSONField(default=list)  # livemap 스타일 좌표
    # 이름 정보
    name = models.CharField(max_length=255, blank=True, default='')

    updated_at = models.DateTimeField()

    # 혼잡도 + 사고 정보 (TMAP 필드명 그대로)
    congestion = models.IntegerField(
        choices=[
            (0, '정보없음'),
            (1, '원활'),
            (2, '서행'),
            (3, '지체'),
            (4, '정체'),
        ],
        default=0
    )
    isAccidentNode = models.CharField(max_length=1, choices=[('Y','Yes'),('N','No')], default='N')
    accidentUpperCode = models.CharField(max_length=5, null=True, blank=True)
    accidentUpperName = models.CharField(max_length=50, null=True, blank=True)
    accidentDetailCode = models.CharField(max_length=5, null=True, blank=True)
    accidentDetailName = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'traffic_current_info'

    def __str__(self):
        return f"{self.name} ({self.coordinate})"

# ==============================================
# TrafficFutureInfo: 예측 교통 정보
# ==============================================
class TrafficFutureInfo(models.Model):
    traffic = models.OneToOneField(
        LiveMapTraffic,
        on_delete=models.CASCADE,
        primary_key=True
    )

    predicted_congestion = models.CharField(
        max_length=10,
        choices=[('low','Low'), ('medium','Medium'), ('high','High')]
    )
    time_set = models.DateTimeField()  # 예측 시점

    class Meta:
        db_table = 'traffic_future_info'

    def __str__(self):
        return f"{self.traffic.name} - {self.time_set} : {self.predicted_congestion}"
