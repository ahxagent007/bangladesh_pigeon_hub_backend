from rest_framework import serializers
from .models import Post, PostImage, Like, Comment


class PostImageSerializer(serializers.ModelSerializer):
    edit_label = serializers.SerializerMethodField()

    class Meta:
        model  = PostImage
        fields = ('id', 'image', 'order', 'edit_score', 'edit_notes', 'edit_label')

    def get_edit_label(self, obj):
        from apps.image_auth import edit_label
        return edit_label(obj.edit_score)


class PostListSerializer(serializers.ModelSerializer):
    author_name   = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    pigeon_name   = serializers.CharField(source='pigeon.name', read_only=True, default=None)
    images        = PostImageSerializer(many=True, read_only=True)
    like_count    = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    is_liked      = serializers.SerializerMethodField()

    class Meta:
        model  = Post
        fields = ('id', 'content', 'author_name', 'author_avatar', 'pigeon_name',
                  'images', 'like_count', 'comment_count', 'is_liked', 'created_at')

    def get_author_avatar(self, obj):
        req = self.context.get('request')
        if obj.author.avatar:
            url = obj.author.avatar.url
            if req and not url.startswith('http'):
                return req.build_absolute_uri(url)
            return url
        return None

    def get_is_liked(self, obj):
        req = self.context.get('request')
        if req and req.user.is_authenticated:
            return obj.likes.filter(user=req.user).exists()
        return False
