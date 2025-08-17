from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

# Post serializer for creating posts
class PostCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False)
    image_url = serializers.CharField(read_only=True)
    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Post
        fields = ['title', 'author', 'content', 'image', 'image_url', 'category', 'latitude', 'longitude', 'location']
        read_only_fields = ['image_url']

    def create(self, validated_data):
        validated_data.pop('image', None)
        validated_data['author'] = self.context['request'].user
        return Post.objects.create(**validated_data)

# Comment serializer for read-only comments in PostDetail
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username') # Display username

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

# Comment serializer for creating comments
class CommentCreateSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ['post', 'content', 'author']
        read_only_fields = ['post']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return Comment.objects.create(**validated_data)

# Post serializer for listing posts
class PostListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username') # Display username
    
    class Meta:
        model = Post
        fields = ['post_id', 'title', 'author', 'location', 'likes', 'created_at']
        read_only_fields = ['post_id', 'created_at']

# Post serializer for detailed view
class PostDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    author = serializers.ReadOnlyField(source='author.username') # Display username
    
    class Meta:
        model = Post
        fields = ['post_id', 'title', 'author', 'content', 'image_url', 'category', 'likes', 'created_at', 'updated_at', 'comments', 'latitude', 'longitude', 'location']
        read_only_fields = ['post_id', 'created_at', 'updated_at']