from django.urls import path
from .views import *

urlpatterns = [
    path('upload/', UploadShelterCSVView.as_view(), name='shelter-upload'),
    path('list/', HeatShelterListView.as_view(), name='shelter-list')
]
