from rest_framework import serializers
from .models import Post, Comment



class PostCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False)
    image_url = serializers.CharField(read_only=True)
    class Meta:
        model = Post
        fields = ['title', 'content', 'image','image_url', 'category', 'latitude', 'longitude','location']
        read_only_fields = ['image_url']

    def create(self,validated_data):
        validated_data.pop('image',None)
        return Post.objects.create(**validated_data)

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['post', 'content']
        read_only_fields = ['post']

class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['post_id','title', 'likes', 'created_at']
        read_only_fields = ['post_id', 'created_at']

class PostDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ['post_id', 'title', 'content', 'image_url', 'category', 'likes', 'created_at', 'updated_at', 'comments', 'latitude', 'longitude','location']
        read_only_fields = ['post_id', 'created_at', 'updated_at']
