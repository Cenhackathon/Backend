from django.apps import AppConfig
from .upload_file import get_csv_path
from .utils.csv_loader import load_shelter_csv

class ShelterConfig(AppConfig):
    name = 'shelter'

    def ready(self):
        csv_path = get_csv_path()
        try:
            load_shelter_csv(csv_path)
            print(f"✅ CSV 자동 로딩 완료: {csv_path}")
        except Exception as e:
            print(f"❌ CSV 로딩 실패: {e}")