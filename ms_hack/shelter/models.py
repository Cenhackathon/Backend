from django.db import models

# Create your models here.
class HeatShelter(models.Model):
    index = models.IntegerField()
    category1 = models.CharField(max_length=50)
    category2 = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    road_address = models.CharField(max_length=200)
    lot_address = models.CharField(max_length=200)
    area = models.FloatField()
    capacity = models.IntegerField()
    note = models.TextField(blank=True, null=True)
    longitude = models.FloatField()
    latitude = models.FloatField()
    x_coord = models.FloatField()
    y_coord = models.FloatField()
