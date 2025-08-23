from django.http import JsonResponse
from django.views import View
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from shelter.models import HeatShelter
from .serializers import HeatShelterSerializer
import csv
import io

# 안전한 숫자 변환 함수
def safe_float(s):
    try:
        return float(s.replace(',', '')) if s and s.strip() != '' else 0.0
    except (ValueError, AttributeError):
        return 0.0

def safe_int(s):
    try:
        return int(float(s.replace(',', ''))) if s and s.strip() != '' else 0
    except (ValueError, AttributeError):
        return 0

# CSV 업로드 뷰
@method_decorator(csrf_exempt, name='dispatch')
class UploadShelterCSVView(View):
    def post(self, request):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return JsonResponse({'error': '파일이 업로드되지 않았습니다.'}, status=400)

        # 파일 내용을 바이트로 읽고 인코딩 시도
        raw_bytes = csv_file.read()
        for enc in ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']:
            try:
                decoded_file = io.StringIO(raw_bytes.decode(enc))
                reader = csv.DictReader(decoded_file)
                break
            except UnicodeDecodeError:
                continue
        else:
            return JsonResponse({'error': '파일 인코딩 오류'}, status=400)

        # DB 저장
        with transaction.atomic():
            for row in reader:
                row = {k.strip(): v.strip() for k, v in row.items() if k}

                HeatShelter.objects.update_or_create(
                    index=safe_int(row.get('계')),  # ✅ CSV 헤더와 정확히 일치
                    defaults={
                        'category1': row.get('시설구분1', ''),
                        'category2': row.get('시설구분2', ''),
                        'name': row.get('쉼터명칭', ''),
                        'road_address': row.get('도로명주소', ''),
                        'lot_address': row.get('지번주소', ''),
                        'area': safe_float(row.get('시설면적')),
                        'capacity': safe_int(row.get('이용가능인원')),
                        'note': row.get('비고', ''),
                        'longitude': safe_float(row.get('경도')),
                        'latitude': safe_float(row.get('위도')),
                        'x_coord': safe_float(row.get('X좌표(EPSG:5186)')),
                        'y_coord': safe_float(row.get('Y좌표(EPSG:5186)')),
                    }
                )

                print(f"✅ 쉼터 저장: {row.get('쉼터명칭', '')}")

        return JsonResponse({'message': '쉼터 정보가 저장되었습니다.'})

# 쉼터 리스트 조회 뷰
class HeatShelterListView(View):
    def get(self, request):
        shelters = HeatShelter.objects.all()
        serializer = HeatShelterSerializer(shelters, many=True)
        return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii': False})