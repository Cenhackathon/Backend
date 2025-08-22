from django.apps import AppConfig

class ShelterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shelter'

    def ready(self):
        # 앱이 완전히 로드된 후에만 import
        from .utils.csv_loader import load_shelter_csv
        # 필요 시 함수 호출도 여기서
        # load_shelter_csv()
