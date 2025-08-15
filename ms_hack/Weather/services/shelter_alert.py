from shelter.models import HeatShelter
from Weather.models import WeatherFutureInfo

def check_shelter_weather_risks(threshold=33):
    alerts = []
    shelters = HeatShelter.objects.all()
    for shelter in shelters:
        forecast = WeatherFutureInfo.objects.filter(
            location_name__icontains="동대문구"
        ).order_by('-time_set').first()

        if forecast and forecast.temperature > threshold:
            alerts.append({
                "shelter": shelter.name,
                "address": shelter.road_address,
                "temperature": forecast.temperature,
                "time": forecast.time_set,
                "risk": "폭염 위험"
            })
    return alerts