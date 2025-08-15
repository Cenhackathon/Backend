from django.urls import path
from .views import UploadShelterCSVView

urlpatterns = [
    path('upload/', UploadShelterCSVView.as_view(), name='shelter-upload'),
]
