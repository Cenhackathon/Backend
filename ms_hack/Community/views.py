import boto3
from uuid import uuid4
from django.conf import settings
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Post


# Create your views here.

class DefaultPageView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer

    def get_queryset(self):
        return self.queryset.order_by('-created_at')

class PostUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer

    def perform_create(self, serializer):
        # Upload the image to S3
        image = self.request.FILES.get('image')
        image_url = None

        if image:
            # boto3 클라이언트 설정
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            region = settings.AWS_S3_REGION_NAME

            # 고유한 파일명 구성
            ext = image.name.split('.')[-1]
            file_key = f"post_images/{uuid4()}.{ext}"

            # S3에 파일 업로드 (기본 private로)
            s3.upload_fileobj(
                image,
                bucket_name,
                file_key,
                ExtraArgs={'ContentType': image.content_type}
            )

            image_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
            serializer.save(image_url=image_url)
        else:
            serializer.save()


class PostListView(generics.ListAPIView):
    serializer_class = PostListSerializer
    def get_queryset(self):
        order_by = self.kwargs.get('order_by', 'created_at')
        category = self.kwargs.get('category')
        queryset = Post.objects.all()

        if category:
            queryset = queryset.filter(category=category)
        return queryset.order_by(f'-{order_by}')

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'post_id'
    lookup_url_kwarg = 'post_id'


class PostDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostDetailSerializer
    lookup_field = 'post_id'
    lookup_url_kwarg = 'post_id'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class PostUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'post_id'
    lookup_url_kwarg = 'post_id'

class CommentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post__post_id=post_id)

class CommentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentCreateSerializer

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, post_id=post_id)
        
        serializer.save(post=post, author=self.request.user)


class LikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, post_id=post_id)
        user = request.user

        like_obj, created = Like.objects.get_or_create(user=user, post=post)

        if created:
            post.likes += 1
        else:
            like_obj.delete()  # 좋아요 객체를 삭제합니다.
            post.likes = max(0, post.likes - 1)  # 좋아요 갯수가 음수가 되지 않도록 방지합니다.

        # 4. 변경된 좋아요 갯수를 데이터베이스에 저장합니다.
        post.save(update_fields=['likes'])

        # 5. 변경된 좋아요 갯수와 상태를 담아 응답을 반환합니다.
        return Response({
            "likes": post.likes,
        }, status=status.HTTP_200_OK)
