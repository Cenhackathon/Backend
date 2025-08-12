from django.urls import path
from .views import *

urlpatterns = [
    path('upload/', PostUploadView.as_view(), name='post-upload'),
    path('list/', PostListView.as_view(), name='post-list'),
    path('<int:post_id>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:post_id>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('<int:post_id>/update/', PostUpdateView.as_view(), name='post-update'),
    path('<int:post_id>/comments/', CommentCreateView.as_view(), name='comment-list'),
    path('<int:post_id>/likes/', LikeIncrementView.as_view(), name='post-likes'),
]