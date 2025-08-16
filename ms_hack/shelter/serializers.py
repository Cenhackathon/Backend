from .models import HeatShelter
from rest_framework import serializers

class HeatShelterSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeatShelter
        fields = '__all__'

    