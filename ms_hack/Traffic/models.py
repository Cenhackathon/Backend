from django.db import models

# Create your models here.

class LiveMapTraffic(models.Model):
    traffic_id = models.AutoField(primary_key=True)
    road_name = models.CharField(max_length=100)
    congestion_level = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ]
    )
    #source_id = models.IntegerField()

    class Meta:
        db_table = 'live_map_traffic'

    def __str__(self):
        return f"{self.road_name} - {self.congestion_level}"

class TrafficCurrentInfo(models.Model):
    traffic_id = models.AutoField(primary_key=True)
    road_name = models.CharField(max_length=100)
    congestion_level = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'traffic_current_info'

    def __str__(self):
        return f"{self.road_name} ({self.latitude}, {self.longitude})"
    
class TrafficFutureInfo(models.Model):
    traffic_id = models.AutoField(primary_key=True)
    road_name = models.CharField(max_length=100)
    congestion_level = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    )
    source_id = models.IntegerField()
    time_set = models.DateTimeField()

    class Meta:
        db_table = 'traffic_future_info'

    def __str__(self):
        return f"{self.road_name} - {self.time_set}"
