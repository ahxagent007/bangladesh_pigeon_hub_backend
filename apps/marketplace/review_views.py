from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Review
from apps.users.models import User
from apps.notifications.models import notify


@login_required
def leave_review(request, username):
    seller = get_object_or_404(User, username=username)
    if seller == request.user:
        messages.error(request, "You can't review yourself.")
        return redirect('public-profile', username=username)

    existing = Review.objects.filter(reviewer=request.user, seller=seller).first()

    if request.method == 'POST':
        rating  = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '').strip()
        if not 1 <= rating <= 5 or not comment:
            messages.error(request, 'Rating and comment are required.')
        else:
            if existing:
                existing.rating  = rating
                existing.comment = comment
                existing.save()
            else:
                Review.objects.create(reviewer=request.user, seller=seller, rating=rating, comment=comment)
                notify(seller, request.user, 'review',
                       f'{request.user.username} left you a {rating}★ review.',
                       f'/users/{seller.username}/')
            messages.success(request, 'Review submitted!')
            return redirect('public-profile', username=username)

    return render(request, 'marketplace/leave_review.html', {
        'seller': seller,
        'existing': existing,
    })
