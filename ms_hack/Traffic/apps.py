from django.apps import AppConfig


class TrafficConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Traffic'

    def ready(self):
        # 앱이 준비되면 auto_update 스레드 시작
        from Traffic.services import auto_update
        auto_update.start_auto_update()