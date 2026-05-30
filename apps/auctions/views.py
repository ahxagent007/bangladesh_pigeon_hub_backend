from decimal import Decimal, InvalidOperation
from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Max, Avg
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Auction, AuctionImage, Bid, AuctionWatch
from apps.pigeons.models import Pigeon
from apps.notifications.models import notify


# ── Public views ─────────────────────────────────────────────────────────────

def auction_list(request):
    now = timezone.now()

    # Auto-sync statuses for auctions that have crossed a boundary
    Auction.objects.filter(status='upcoming', start_time__lte=now).update(status='live')
    live_ids = Auction.objects.filter(status='live', end_time__lte=now).values_list('pk', flat=True)
    for pk in live_ids:
        Auction.objects.get(pk=pk)._finalize()   # handles notifications + ownership

    live     = Auction.objects.filter(status='live').select_related('seller','pigeon').prefetch_related('pigeon__images').order_by('end_time')
    upcoming = Auction.objects.filter(status='upcoming').select_related('seller','pigeon').prefetch_related('pigeon__images').order_by('start_time')
    ended    = Auction.objects.filter(status='ended').select_related('seller','winner','pigeon').prefetch_related('pigeon__images').order_by('-end_time')[:12]

    return render(request, 'auctions/list.html', {
        'live': live,
        'upcoming': upcoming,
        'ended': ended,
    })


def auction_detail(request, pk):
    auction = get_object_or_404(
        Auction.objects.select_related('seller', 'pigeon__breed', 'winner')
                       .prefetch_related('gallery', 'pigeon__images', 'bids__bidder'),
        pk=pk
    )
    auction.sync_status()
    auction.increment_views()

    bids         = auction.bids.select_related('bidder').order_by('-created_at')[:30]
    gallery_imgs = auction.get_all_gallery_images()
    pedigree_img = (
        auction.pedigree_image
        or (auction.pigeon.pedigree_image if auction.pigeon else None)
    )
    is_watching  = False
    user_top_bid = None
    is_top_bidder = False

    if request.user.is_authenticated:
        is_watching   = AuctionWatch.objects.filter(auction=auction, user=request.user).exists()
        user_top_bid  = auction.bids.filter(bidder=request.user).order_by('-amount').first()
        top_bid       = auction.bids.order_by('-amount').first()
        is_top_bidder = bool(top_bid and top_bid.bidder == request.user)

    return render(request, 'auctions/detail.html', {
        'auction':       auction,
        'gallery_imgs':  gallery_imgs,
        'pedigree_img':  pedigree_img,
        'bids':          bids,
        'is_watching':   is_watching,
        'user_top_bid':  user_top_bid,
        'is_top_bidder': is_top_bidder,
        'min_bid':       auction.min_next_bid,
    })


# ── Bid (AJAX) ────────────────────────────────────────────────────────────────

@login_required
@require_POST
def place_bid(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    auction.sync_status()

    if auction.seller == request.user:
        return JsonResponse({'error': "You can't bid on your own auction."}, status=400)
    if auction.status != 'live':
        return JsonResponse({'error': 'Auction is not active.'}, status=400)

    try:
        amount = Decimal(request.POST.get('amount', '0'))
    except InvalidOperation:
        return JsonResponse({'error': 'Invalid amount.'}, status=400)

    if amount < auction.min_next_bid:
        return JsonResponse({'error': f'Minimum bid is BDT {auction.min_next_bid:,.0f}.'}, status=400)

    # Previous top bidder (to notify)
    prev_top = auction.bids.order_by('-amount').first()

    # Create bid
    Bid.objects.create(auction=auction, bidder=request.user, amount=amount)

    # Update auction price + count
    auction.current_price = amount
    auction.bid_count     = auction.bid_count + 1

    # Anti-snipe: extend end_time if bid lands in last N minutes
    snipe_window = timezone.timedelta(minutes=auction.anti_snipe_min)
    extended     = False
    if timezone.now() > auction.end_time - snipe_window:
        auction.end_time = timezone.now() + snipe_window
        extended = True

    auction.save(update_fields=['current_price', 'bid_count', 'end_time'])

    # Notify outbid user
    if prev_top and prev_top.bidder != request.user:
        notify(
            prev_top.bidder, request.user, 'offer_countered',
            f'You were outbid on "{auction.title}". New price: BDT {amount:,.0f}.',
            f'/auctions/{pk}/',
        )

    # Notify seller
    notify(
        auction.seller, request.user, 'offer_received',
        f'{request.user.username} bid BDT {amount:,.0f} on "{auction.title}".',
        f'/auctions/{pk}/dashboard/',
    )

    return JsonResponse({
        'success':       True,
        'current_price': str(amount),
        'bid_count':     auction.bid_count,
        'min_bid':       str(auction.min_next_bid),
        'end_time_iso':  auction.end_time.isoformat(),
        'end_seconds':   auction.seconds_remaining,
        'extended':      extended,
        'bidder':        request.user.username,
    })


# ── Live poll (5 s) ───────────────────────────────────────────────────────────

def auction_poll(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    auction.sync_status()
    top = auction.bids.order_by('-amount').first()
    return JsonResponse({
        'status':        auction.status,
        'current_price': str(auction.display_price),
        'bid_count':     auction.bid_count,
        'end_seconds':   auction.seconds_remaining,
        'end_time_iso':  auction.end_time.isoformat(),
        'winner':        auction.winner.username if auction.winner else None,
        'top_bidder':    top.bidder.username if top else None,
        'min_bid':       str(auction.min_next_bid),
        'reserve_met':   auction.reserve_met,
    })


# ── Watch ─────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def toggle_watch(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    watch, created = AuctionWatch.objects.get_or_create(auction=auction, user=request.user)
    if not created:
        watch.delete()
    return JsonResponse({'watching': created, 'watchers': auction.watchers.count()})


# ── Create ────────────────────────────────────────────────────────────────────

@login_required
def create_auction(request):
    user_pigeons = Pigeon.objects.filter(owner=request.user).select_related('breed').order_by('name')

    if request.method == 'POST':
        title          = request.POST.get('title', '').strip()
        description    = request.POST.get('description', '').strip()
        starting_price = request.POST.get('starting_price')
        reserve_price  = request.POST.get('reserve_price') or None
        min_increment  = request.POST.get('min_increment') or '50'
        start_time     = request.POST.get('start_time')
        end_time       = request.POST.get('end_time')
        pigeon_id       = request.POST.get('pigeon_id') or None
        main_image      = request.FILES.get('main_image')
        gallery_files   = request.FILES.getlist('gallery_images')
        pedigree_file   = request.FILES.get('pedigree_image')
        anti_snipe_min  = int(request.POST.get('anti_snipe_min', 2))

        errors = []
        if not title:           errors.append('Title is required.')
        if not description:     errors.append('Description is required.')
        if not starting_price:  errors.append('Starting price is required.')
        if not start_time:      errors.append('Start time is required.')
        if not end_time:        errors.append('End time is required.')
        if not pigeon_id and not main_image:
            errors.append('Select a pigeon from your flock or upload a main photo.')

        if not errors:
            try:
                from django.utils.dateparse import parse_datetime
                from django.utils.timezone import make_aware, get_current_timezone

                def _parse(s):
                    """Handle YYYY-MM-DDTHH:MM from datetime-local inputs."""
                    if not s:
                        return None
                    # Pad missing seconds
                    if len(s) == 16:
                        s = s + ':00'
                    dt = parse_datetime(s)
                    if dt is None:
                        return None
                    # Make timezone-aware if naive
                    if timezone.is_naive(dt):
                        dt = make_aware(dt, get_current_timezone())
                    return dt

                st = _parse(start_time)
                et = _parse(end_time)
                if not st or not et:
                    raise ValueError('Could not parse datetime')
                if et <= st:
                    errors.append('End time must be after start time.')
                if et <= timezone.now():
                    errors.append('End time must be in the future.')
            except (ValueError, TypeError):
                errors.append('Invalid date/time format.')

        if not errors:
            pigeon = None
            if pigeon_id:
                try:
                    pigeon = Pigeon.objects.get(pk=pigeon_id, owner=request.user)
                except Pigeon.DoesNotExist:
                    errors.append('Invalid pigeon selection.')

        if not errors:
            status = 'upcoming' if st > timezone.now() else 'live'
            auction = Auction.objects.create(
                seller         = request.user,
                pigeon         = pigeon,
                title          = title,
                description    = description,
                image          = main_image,
                pedigree_image = pedigree_file,
                starting_price = Decimal(starting_price),
                reserve_price  = Decimal(reserve_price) if reserve_price else None,
                min_increment  = Decimal(min_increment),
                start_time     = st,
                end_time       = et,
                anti_snipe_min = anti_snipe_min,
                status         = status,
            )
            # Save additional gallery images
            for i, f in enumerate(gallery_files[:10]):   # cap at 10
                AuctionImage.objects.create(auction=auction, image=f, order=i)

            messages.success(request, f'Auction "{auction.title}" created!')
            return redirect('auction-detail', pk=auction.pk)

        for e in errors:
            messages.error(request, e)

    return render(request, 'auctions/create.html', {'user_pigeons': user_pigeons})


# ── My Auctions (seller list) ─────────────────────────────────────────────────

@login_required
def my_auctions(request):
    auctions = Auction.objects.filter(seller=request.user).order_by('-created_at')
    for a in auctions:
        a.sync_status()
    return render(request, 'auctions/my_auctions.html', {'auctions': auctions})


# ── Auction Insights Dashboard ────────────────────────────────────────────────

@login_required
def auction_dashboard(request, pk):
    auction = get_object_or_404(Auction, pk=pk, seller=request.user)
    auction.sync_status()

    bids_qs = auction.bids.select_related('bidder').order_by('created_at')
    bids    = list(bids_qs)

    # Bid timeline — group by hour bucket
    timeline = defaultdict(int)
    for bid in bids:
        bucket = bid.created_at.strftime('%d/%m %H:00')
        timeline[bucket] += 1
    timeline = dict(timeline)
    max_bucket = max(timeline.values(), default=1)

    # Bidder leaderboard
    bidder_stats = (
        bids_qs.values('bidder__username')
               .annotate(bid_count=Count('id'), top_bid=Max('amount'))
               .order_by('-top_bid')
    )

    # Price progression (start + each bid)
    price_points = [(auction.start_time, auction.starting_price)] + \
                   [(b.created_at, b.amount) for b in bids]
    price_max    = max((p[1] for p in price_points), default=auction.starting_price)

    stats = {
        'total_bids':      len(bids),
        'unique_bidders':  bids_qs.values('bidder').distinct().count(),
        'watchers':        auction.watchers.count(),
        'views':           auction.views_count,
        'price_increase':  round(
            float((auction.display_price - auction.starting_price) / auction.starting_price * 100), 1
        ) if auction.starting_price else 0,
    }

    # End-early / cancel actions
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'cancel' and len(bids) == 0 and auction.status in ('upcoming', 'live'):
            auction.status = 'cancelled'
            auction.save(update_fields=['status'])
            messages.success(request, 'Auction cancelled.')
            return redirect('my-auctions')
        elif action == 'end_early' and auction.status == 'live':
            auction._finalize()
            messages.success(request, 'Auction ended early.')
            return redirect('auction-dashboard', pk=pk)

    return render(request, 'auctions/dashboard.html', {
        'auction':       auction,
        'bids':          bids,
        'stats':         stats,
        'timeline':      timeline,
        'max_bucket':    max_bucket,
        'bidder_stats':  bidder_stats,
        'price_points':  price_points,
        'price_max':     price_max,
    })
