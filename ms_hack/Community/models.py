from django.db import models
from django.conf import settings

# Create your models here.

#게시물 모델
class Post(models.Model):
    CATEGORY_CHOICES = [
        ('notice', '공지'),
        ('emergency', '긴급'),
        ('general', '일반'),
    ]

    post_id = models.AutoField(primary_key=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 작성자
    title = models.CharField(max_length=200)
    latitude = models.FloatField(blank=True, null=True)  # 위도
    longitude = models.FloatField(blank=True, null=True)  # 경도
    location = models.TextField(blank=True, null=True)  # 위치 정보
    content = models.TextField()
    image_url = models.URLField(blank=True, null=True)  # 이미지 URL
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# 댓글 모델
class Comment (models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  # FK: 게시글
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.id} on {self.post}"