from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import User, Follow
from apps.marketplace.models import Listing, Review
from apps.wall.models import Post
from apps.notifications.models import notify


def public_profile(request, username):
    from apps.auctions.models import Auction
    profile_user = get_object_or_404(User, username=username)
    listings     = Listing.objects.filter(seller=profile_user, status='active').prefetch_related('pigeon__images')[:6]
    reviews      = Review.objects.filter(seller=profile_user).select_related('reviewer')[:10]
    posts        = Post.objects.filter(author=profile_user).prefetch_related('images')[:6]
    won_auctions = Auction.objects.filter(winner=profile_user, status='ended').select_related('pigeon__breed')[:6]
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    return render(request, 'users/public_profile.html', {
        'profile_user': profile_user,
        'listings':     listings,
        'reviews':      reviews,
        'posts':        posts,
        'won_auctions': won_auctions,
        'is_following': is_following,
        'avg_rating':   profile_user.avg_rating,
    })


@login_required
@require_POST
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
        following = False
    else:
        following = True
        notify(target, request.user, 'follow',
               f'{request.user.username} started following you.',
               f'/users/{request.user.username}/')

    return JsonResponse({
        'following': following,
        'follower_count': target.follower_count,
    })
