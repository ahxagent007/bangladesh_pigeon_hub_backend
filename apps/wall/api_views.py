from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Post, PostImage, Like, Comment
from .serializers import PostListSerializer


class WallPostListView(generics.ListAPIView):
    serializer_class   = PostListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (Post.objects
                .select_related('author', 'pigeon')
                .prefetch_related('images', 'likes', 'comments')
                .order_by('-created_at')[:30])


class ToggleLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = Post.objects.get(pk=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
        return Response({'liked': created, 'like_count': post.like_count})
