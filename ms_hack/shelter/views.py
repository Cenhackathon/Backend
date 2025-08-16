from django.shortcuts import render
import csv
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from shelter.models import HeatShelter
from .serializers import HeatShelterSerializer

def safe_float(s):
    try:
        return float(s.replace(',', '')) if s and s.strip() != '' else 0.0
    except:
        return 0.0

def safe_int(s):
    try:
        return int(float(s.replace(',', ''))) if s and s.strip() != '' else 0
    except:
        return 0

class UploadShelterCSVView(View):
    def post(self, request):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return JsonResponse({'error': '파일이 업로드되지 않았습니다.'}, status=400)

        # 인코딩 처리
        for enc in ['cp949', 'euc-kr', 'utf-8']:
            try:
                decoded_file = csv_file.read().decode(enc).splitlines()
                break
            except UnicodeDecodeError:
                continue
        else:
            return JsonResponse({'error': '파일 인코딩 오류'}, status=400)

        reader = csv.DictReader(decoded_file)
        
        # 트랜잭션으로 묶어서 SQLite 잠금 방지
        with transaction.atomic():
            for row in reader:
                # 컬럼명 공백 제거
                row = {k.strip(): v for k, v in row.items()}

                HeatShelter.objects.update_or_create(
                    index=int(row.get('시설코드', 0)),
                    defaults={
                        'category1': row.get('시설구분1', ''),
                        'category2': row.get('시설구분2', ''),
                        'name': row.get('쉼터명칭', ''),
                        'road_address': row.get('도로명주소', ''),
                        'lot_address': row.get('지번주소', ''),
                        'area': safe_float(row.get('시설면적', '0')),
                        'capacity': safe_int(row.get('이용가능인원', '0')),
                        'note': row.get('비고', ''),
                        'longitude': safe_float(row.get('경도', '0')),
                        'latitude': safe_float(row.get('위도', '0')),
                        'x_coord': safe_float(row.get('X좌표', '0')),
                        'y_coord': safe_float(row.get('Y좌표', '0')),
                    }
                )

        return JsonResponse({'message': '쉼터 정보가 저장되었습니다.'})


class HeatShelterListView(View):
    def get(self, request):
        shelters = HeatShelter.objects.all()
        serializer = HeatShelterSerializer(shelters, many=True)
        return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})