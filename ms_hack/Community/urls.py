from django.urls import path
from .views import *

urlpatterns = [
    path('', DefaultPageView.as_view(), name='default-page'),
    path('upload/', PostUploadView.as_view(), name='post-upload'),
    path('list/<str:order_by>/', PostListView.as_view(), name='post-list-order'),
    path('list/<str:order_by>/<str:category>/', PostListView.as_view(), name='post-list'),
    path('<int:post_id>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:post_id>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('<int:post_id>/update/', PostUpdateView.as_view(), name='post-update'),
    path('<int:post_id>/comments/', CommentCreateView.as_view(), name='comment-list'),
    path('<int:post_id>/likes/', LikeToggleView.as_view(), name='post-likes'),
]