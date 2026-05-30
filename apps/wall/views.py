import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.timesince import timesince
from django.db.models import Prefetch, Exists, OuterRef
from .models import Post, PostImage, Like, Comment
from apps.pigeons.models import Pigeon


def _post_to_dict(post, user):
    """Serialize a Post for JSON responses."""
    liked = post.likes.filter(user=user).exists() if user.is_authenticated else False
    imgs  = [{'url': img.image.url} for img in post.images.all()]
    pigeon = None
    if post.pigeon:
        pigeon = {
            'name': post.pigeon.name,
            'breed': post.pigeon.breed.name if post.pigeon.breed else 'Unknown Breed',
            'url': f'/pigeons/{post.pigeon.pk}/',
            'img': post.pigeon.primary_image.image.url if post.pigeon.primary_image else None,
        }
    return {
        'id': post.pk,
        'content': post.content,
        'like_count': post.like_count,
        'comment_count': post.comment_count,
        'liked': liked,
        'images': imgs,
        'pigeon': pigeon,
        'author': {
            'username': post.author.username,
            'avatar': post.author.avatar.url if post.author.avatar else None,
            'initial': post.author.username[0].upper(),
        },
        'time_ago': timesince(post.created_at) + ' ago',
    }


def wall_feed(request):
    posts_qs = (
        Post.objects
        .select_related('author', 'pigeon__breed')
        .prefetch_related(
            'images',
            Prefetch('likes'),
            Prefetch('comments', queryset=Comment.objects.select_related('author').order_by('created_at')),
        )
        .order_by('-created_at')
    )

    # Annotate liked status for authenticated user
    liked_post_ids = set()
    if request.user.is_authenticated:
        liked_post_ids = set(
            Like.objects.filter(user=request.user).values_list('post_id', flat=True)
        )

    user_pigeons = []
    if request.user.is_authenticated:
        user_pigeons = Pigeon.objects.filter(owner=request.user).select_related('breed').order_by('name')

    return render(request, 'wall/feed.html', {
        'posts': posts_qs[:30],
        'liked_post_ids': liked_post_ids,
        'user_pigeons': user_pigeons,
    })


@login_required
@require_POST
def create_post(request):
    content = request.POST.get('content', '').strip()
    if not content:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Post cannot be empty.'}, status=400)
        return redirect('wall-feed')

    pigeon_id = request.POST.get('pigeon_id') or None
    pigeon = None
    if pigeon_id:
        try:
            pigeon = Pigeon.objects.get(pk=pigeon_id, owner=request.user)
        except Pigeon.DoesNotExist:
            pass

    post = Post.objects.create(author=request.user, content=content, pigeon=pigeon)

    for i, f in enumerate(request.FILES.getlist('images')):
        PostImage.objects.create(post=post, image=f, order=i)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post.refresh_from_db()
        return JsonResponse({'post': _post_to_dict(post, request.user)})

    return redirect('wall-feed')


@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({'liked': liked, 'like_count': post.like_count})


@login_required
@require_POST
def add_comment(request, post_id):
    post    = get_object_or_404(Post, pk=post_id)
    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'error': 'Comment cannot be empty.'}, status=400)

    comment = Comment.objects.create(author=request.user, post=post, content=content)
    return JsonResponse({
        'id': comment.pk,
        'content': comment.content,
        'time_ago': timesince(comment.created_at) + ' ago',
        'author': {
            'username': comment.author.username,
            'avatar': comment.author.avatar.url if comment.author.avatar else None,
            'initial': comment.author.username[0].upper(),
        },
        'comment_count': post.comment_count,
    })


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    post.delete()
    return JsonResponse({'deleted': True})


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    post_id = comment.post_id
    comment.delete()
    post = Post.objects.get(pk=post_id)
    return JsonResponse({'deleted': True, 'comment_count': post.comment_count})
