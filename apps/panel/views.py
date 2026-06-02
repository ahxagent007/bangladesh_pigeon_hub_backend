import functools
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden

from apps.users.models import User
from apps.marketplace.models import Listing, Offer, Payment, BD_DISTRICTS
from apps.auctions.models import Auction, Bid
from apps.wall.models import Post
from apps.notifications.models import Notification


def panel_required(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/auth/login/?next={request.path}')
        if not (request.user.is_staff or request.user.is_superuser):
            return HttpResponseForbidden("You don't have permission to access the admin panel.")
        return view_func(request, *args, **kwargs)
    return wrapper


# ── Dashboard ────────────────────────────────────────────────────────────────

@panel_required
def dashboard(request):
    ctx = {
        'stats': {
            'total_users':        User.objects.count(),
            'active_users':       User.objects.filter(is_active=True).count(),
            'verified_users':     User.objects.filter(is_verified=True).count(),
            'total_listings':     Listing.objects.count(),
            'active_listings':    Listing.objects.filter(status='active').count(),
            'sold_listings':      Listing.objects.filter(status='sold').count(),
            'total_auctions':     Auction.objects.count(),
            'live_auctions':      Auction.objects.filter(status='live').count(),
            'pending_offers':     Offer.objects.filter(status='pending').count(),
            'accepted_offers':    Offer.objects.filter(status='accepted').count(),
            'pending_payments':   Payment.objects.filter(status='pending').count(),
            'confirmed_payments': Payment.objects.filter(status='confirmed').count(),
            'total_wall_posts':   Post.objects.count(),
            'unread_notifs':      Notification.objects.filter(is_read=False).count(),
        },
        'recent_users':    User.objects.order_by('-date_joined')[:6],
        'recent_listings': Listing.objects.select_related('seller', 'pigeon__breed').order_by('-created_at')[:6],
        'recent_auctions': Auction.objects.select_related('seller').order_by('-created_at')[:5],
        'recent_offers':   Offer.objects.select_related('buyer', 'listing').order_by('-created_at')[:5],
        'recent_payments': Payment.objects.select_related('buyer', 'offer__listing').order_by('-created_at')[:5],
    }
    return render(request, 'panel/dashboard.html', ctx)


# ── Users ─────────────────────────────────────────────────────────────────────

@panel_required
def users(request):
    q         = request.GET.get('q', '').strip()
    filter_by = request.GET.get('filter', '')

    qs = User.objects.annotate(
        num_listings=Count('listings', distinct=True),
        num_auctions=Count('auctions', distinct=True),
    ).order_by('-date_joined')

    if q:
        qs = qs.filter(
            Q(username__icontains=q) | Q(email__icontains=q) |
            Q(phone__icontains=q)   | Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )
    if filter_by == 'staff':
        qs = qs.filter(is_staff=True)
    elif filter_by == 'inactive':
        qs = qs.filter(is_active=False)
    elif filter_by == 'verified':
        qs = qs.filter(is_verified=True)
    elif filter_by == 'unverified':
        qs = qs.filter(is_verified=False, is_active=True)

    paginator = Paginator(qs, 30)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'panel/users.html', {
        'page_obj': page_obj, 'q': q, 'filter_by': filter_by,
        'total': paginator.count,
    })


@panel_required
def user_detail(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    return render(request, 'panel/user_detail.html', {
        'u':           u,
        'listings':    Listing.objects.filter(seller=u).select_related('pigeon__breed').order_by('-created_at')[:10],
        'auctions':    Auction.objects.filter(seller=u).order_by('-created_at')[:10],
        'bids':        Bid.objects.filter(bidder=u).select_related('auction').order_by('-created_at')[:10],
        'offers_sent': Offer.objects.filter(buyer=u).select_related('listing').order_by('-created_at')[:10],
        'posts':       Post.objects.filter(author=u).order_by('-created_at')[:10],
    })


@panel_required
@require_POST
def toggle_user(request, user_id):
    u      = get_object_or_404(User, pk=user_id)
    action = request.POST.get('action')

    if action == 'active':
        u.is_active = not u.is_active
        u.save(update_fields=['is_active'])
        messages.success(request, f"{'Activated' if u.is_active else 'Deactivated'} {u.username}.")
    elif action == 'verified':
        u.is_verified = not u.is_verified
        u.save(update_fields=['is_verified'])
        messages.success(request, f"{'Verified' if u.is_verified else 'Unverified'} {u.username}.")
    elif action == 'staff' and request.user.is_superuser:
        u.is_staff = not u.is_staff
        u.save(update_fields=['is_staff'])
        messages.success(request, f"{'Granted' if u.is_staff else 'Revoked'} staff for {u.username}.")

    return redirect(request.POST.get('next', '/panel/users/'))


# ── Listings ──────────────────────────────────────────────────────────────────

@panel_required
def listings(request):
    q          = request.GET.get('q', '').strip()
    status_f   = request.GET.get('status', '')
    district_f = request.GET.get('district', '')

    qs = Listing.objects.select_related('seller', 'pigeon__breed').order_by('-created_at')
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(seller__username__icontains=q) |
            Q(pigeon__name__icontains=q)
        )
    if status_f:
        qs = qs.filter(status=status_f)
    if district_f:
        qs = qs.filter(district=district_f)

    paginator = Paginator(qs, 30)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'panel/listings.html', {
        'page_obj': page_obj, 'q': q, 'status_f': status_f,
        'district_f': district_f, 'total': paginator.count,
        'districts': BD_DISTRICTS,
        'status_choices': Listing.STATUS_CHOICES,
    })


@panel_required
@require_POST
def listing_status(request, pk):
    listing   = get_object_or_404(Listing, pk=pk)
    new_status = request.POST.get('status')
    valid = {k for k, _ in Listing.STATUS_CHOICES}
    if new_status in valid:
        listing.status = new_status
        listing.save(update_fields=['status'])
        messages.success(request, f'Listing "{listing.title}" → {new_status}.')
    return redirect('/panel/listings/')


@panel_required
@require_POST
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    title   = listing.title
    listing.delete()
    messages.success(request, f'Listing "{title}" deleted.')
    return redirect('/panel/listings/')


# ── Auctions ─────────────────────────────────────────────────────────────────

@panel_required
def auctions(request):
    q        = request.GET.get('q', '').strip()
    status_f = request.GET.get('status', '')

    qs = Auction.objects.select_related('seller', 'pigeon__breed', 'winner').order_by('-created_at')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(seller__username__icontains=q))
    if status_f:
        qs = qs.filter(status=status_f)

    paginator = Paginator(qs, 30)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'panel/auctions.html', {
        'page_obj': page_obj, 'q': q, 'status_f': status_f, 'total': paginator.count,
    })


@panel_required
@require_POST
def auction_cancel(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    if auction.status not in ('ended', 'cancelled'):
        auction.status = 'cancelled'
        auction.save(update_fields=['status'])
        messages.success(request, f'Auction "{auction.title}" cancelled.')
    else:
        messages.warning(request, 'Auction is already ended or cancelled.')
    return redirect('/panel/auctions/')


# ── Offers ────────────────────────────────────────────────────────────────────

@panel_required
def offers(request):
    q        = request.GET.get('q', '').strip()
    status_f = request.GET.get('status', '')

    qs = Offer.objects.select_related(
        'buyer', 'listing__seller', 'listing__pigeon__breed'
    ).order_by('-created_at')
    if q:
        qs = qs.filter(Q(buyer__username__icontains=q) | Q(listing__title__icontains=q))
    if status_f:
        qs = qs.filter(status=status_f)

    paginator = Paginator(qs, 30)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'panel/offers.html', {
        'page_obj': page_obj, 'q': q, 'status_f': status_f, 'total': paginator.count,
        'offer_statuses': Offer.STATUS,
    })


# ── Payments ──────────────────────────────────────────────────────────────────

@panel_required
def payments(request):
    q        = request.GET.get('q', '').strip()
    status_f = request.GET.get('status', '')

    qs = Payment.objects.select_related(
        'buyer', 'offer__listing__seller', 'offer__listing'
    ).order_by('-created_at')
    if q:
        qs = qs.filter(Q(buyer__username__icontains=q) | Q(trx_id__icontains=q))
    if status_f:
        qs = qs.filter(status=status_f)

    paginator = Paginator(qs, 30)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'panel/payments.html', {
        'page_obj': page_obj, 'q': q, 'status_f': status_f, 'total': paginator.count,
    })


@panel_required
@require_POST
def payment_action(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    action  = request.POST.get('action')
    if action in ('confirmed', 'disputed'):
        payment.status = action
        payment.save(update_fields=['status'])
        messages.success(request, f'Payment #{pk} marked as {action}.')
    return redirect('/panel/payments/')


# ── Wall ──────────────────────────────────────────────────────────────────────

@panel_required
def wall_posts(request):
    q  = request.GET.get('q', '').strip()
    qs = Post.objects.select_related('author', 'pigeon').order_by('-created_at')
    if q:
        qs = qs.filter(Q(author__username__icontains=q) | Q(content__icontains=q))

    paginator = Paginator(qs, 30)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'panel/wall.html', {
        'page_obj': page_obj, 'q': q, 'total': paginator.count,
    })


@panel_required
@require_POST
def wall_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('/panel/wall/')


# ── Notifications ─────────────────────────────────────────────────────────────

@panel_required
def notifications(request):
    q      = request.GET.get('q', '').strip()
    type_f = request.GET.get('type', '')

    qs = Notification.objects.select_related('recipient', 'actor').order_by('-created_at')
    if q:
        qs = qs.filter(Q(recipient__username__icontains=q) | Q(message__icontains=q))
    if type_f:
        qs = qs.filter(notif_type=type_f)

    paginator = Paginator(qs, 40)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'panel/notifications.html', {
        'page_obj': page_obj, 'q': q, 'type_f': type_f, 'total': paginator.count,
        'notif_types': Notification.TYPES,
    })
