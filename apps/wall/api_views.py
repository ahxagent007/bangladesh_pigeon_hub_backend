from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Post, PostImage, Like, Comment
from .serializers import PostListSerializer, CommentSerializer
from apps.pigeons.models import Pigeon


class WallPostListView(generics.ListAPIView):
    serializer_class   = PostListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (Post.objects
                .select_related('author', 'pigeon')
                .prefetch_related('images', 'likes', 'comments')
                .order_by('-created_at')[:30])

    def get_serializer_context(self):
        return {'request': self.request}


class CreatePostView(APIView):
    """POST /api/wall/  — create a post with optional pigeon tag + images."""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        content = request.data.get('content', '').strip()
        if not content:
            return Response({'error': 'Post cannot be empty.'}, status=400)

        pigeon = None
        pigeon_id = request.data.get('pigeon_id') or None
        if pigeon_id:
            pigeon = Pigeon.objects.filter(pk=pigeon_id, owner=request.user).first()

        post = Post.objects.create(author=request.user, content=content, pigeon=pigeon)

        for i, f in enumerate(request.FILES.getlist('images')):
            PostImage.objects.create(post=post, image=f, order=i)

        post.refresh_from_db()
        return Response(
            PostListSerializer(post, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class ToggleLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
        return Response({'liked': created, 'like_count': post.like_count})


class CommentListCreateView(APIView):
    """GET + POST /api/wall/<post_id>/comments/"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        comments = post.comments.select_related('author').order_by('created_at')
        return Response(
            CommentSerializer(comments, many=True, context={'request': request}).data
        )

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        content = request.data.get('content', '').strip()
        if not content:
            return Response({'error': 'Comment cannot be empty.'}, status=400)

        comment = Comment.objects.create(author=request.user, post=post, content=content)

        if post.author != request.user:
            from apps.notifications.models import notify
            notify(post.author, request.user, 'comment',
                   f'{request.user.username} commented on your post.', '/wall/')

        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class CommentDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
