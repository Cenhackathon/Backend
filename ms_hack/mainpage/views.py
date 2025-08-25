from rest_framework.generics import ListAPIView
from Community.models import Post
from Community.serializers import PostDetailSerializer

class PopularPostsView(ListAPIView):
    serializer_class = PostDetailSerializer
    def get_queryset(self):
        return Post.objects.filter(likes__gte=3).order_by('-created_at')[:5]

