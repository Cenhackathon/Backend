from django.shortcuts import render

# Create your views here.
import csv
from django.views import View
from django.http import JsonResponse
from .models import HeatShelter

class UploadShelterCSVView(View):
    def post(self, request):
        csv_file = request.FILES['file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        for row in reader:
            HeatShelter.objects.update_or_create(
                index=int(row['계']),
                defaults={
                    'category1': row['시설구분1'],
                    'category2': row['시설구분2'],
                    'name': row['쉼터명칭'],
                    'road_address': row['도로명주소'],
                    'lot_address': row['지번주소'],
                    'area': float(row['시설면적']),
                    'capacity': int(row['이용가능 인구']),
                    'note': row['비고'],
                    'longitude': float(row['경도']),
                    'latitude': float(row['위도']),
                    'x_coord': float(row['X좌표']),
                    'y_coord': float(row['Y좌표']),
                }
            )
        return JsonResponse({'message': '쉼터 정보가 저장되었습니다.'})
