from django.urls import path, include

app_name = 'accounts'

from django.urls import path, include

urlpatterns = [
    # 기존 URL에 'api/auth/' 접두사 추가
    path('', include('dj_rest_auth.urls')),
    path('registration/', include('dj_rest_auth.registration.urls')),
]