import csv
from shelter.models import HeatShelter

def load_shelter_csv(path):
    for enc in ['utf-8', 'cp949', 'euc-kr']:
        try:
            with open(path, newline='', encoding=enc) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    HeatShelter.objects.update_or_create(
                        name=row["시설명"],
                        defaults={
                            "latitude": float(row["위도"]),
                            "longitude": float(row["경도"]),
                            "location": row["주소"],
                            "capacity": int(row["수용인원"]),
                            "type": row["분류"]
                        }
                    )
                print(f"✅ CSV 로딩 성공 (인코딩: {enc})")
                break
        except UnicodeDecodeError:
            print(f"⚠️ 인코딩 실패: {enc}")
            continue
        except Exception as e:
            print(f"❌ CSV 처리 중 오류 발생: {e}")
            break
    else:
        print("❌ 모든 인코딩 시도 실패: 파일을 읽을 수 없습니다.")