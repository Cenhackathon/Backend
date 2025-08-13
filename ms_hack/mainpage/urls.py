from django.urls import path
from .views import PopularPostsView

urlpatterns = [
    path('pop/', PopularPostsView.as_view(), name='popular-posts'),
    
]