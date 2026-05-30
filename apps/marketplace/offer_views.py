from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Listing, Offer, Payment
from apps.notifications.models import notify


@login_required
def make_offer(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id, status='active')
    if listing.seller == request.user:
        messages.error(request, "You can't offer on your own listing.")
        return redirect('listing-detail', pk=listing_id)

    existing = Offer.objects.filter(listing=listing, buyer=request.user, status='pending').first()
    if request.method == 'POST':
        amount  = request.POST.get('amount')
        message = request.POST.get('message', '').strip()
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, 'Enter a valid amount.')
            return redirect('make-offer', listing_id=listing_id)

        if existing:
            existing.amount  = amount
            existing.message = message
            existing.save()
        else:
            Offer.objects.create(listing=listing, buyer=request.user, amount=amount, message=message)
        notify(listing.seller, request.user, 'offer_received',
               f'{request.user.username} made an offer of BDT {amount:,.0f} on "{listing.title}".',
               f'/offers/')
        messages.success(request, 'Offer sent!')
        return redirect('listing-detail', pk=listing_id)

    return render(request, 'marketplace/make_offer.html', {
        'listing': listing,
        'existing': existing,
    })


@login_required
def my_offers(request):
    sent     = Offer.objects.filter(buyer=request.user).select_related('listing__pigeon').order_by('-created_at')
    received = Offer.objects.filter(listing__seller=request.user).select_related('listing','buyer').order_by('-created_at')
    return render(request, 'marketplace/my_offers.html', {'sent': sent, 'received': received})


@login_required
@require_POST
def respond_offer(request, offer_id):
    offer  = get_object_or_404(Offer, pk=offer_id, listing__seller=request.user, status='pending')
    action = request.POST.get('action')

    if action == 'accept':
        offer.status = 'accepted'
        offer.save()
        notify(offer.buyer, request.user, 'offer_accepted',
               f'Your offer on "{offer.listing.title}" was accepted! 🎉',
               f'/offers/')
    elif action == 'reject':
        offer.status = 'rejected'
        offer.save()
        notify(offer.buyer, request.user, 'offer_rejected',
               f'Your offer on "{offer.listing.title}" was declined.',
               f'/offers/')
    elif action == 'counter':
        counter_amount = request.POST.get('counter_amount')
        counter_msg    = request.POST.get('counter_msg', '')
        try:
            counter_amount = float(counter_amount)
        except (TypeError, ValueError):
            messages.error(request, 'Invalid counter amount.')
            return redirect('my-offers')
        offer.status         = 'countered'
        offer.counter_amount = counter_amount
        offer.counter_msg    = counter_msg
        offer.save()
        notify(offer.buyer, request.user, 'offer_countered',
               f'Counter offer of BDT {counter_amount:,.0f} on "{offer.listing.title}".',
               f'/offers/')

    messages.success(request, 'Response sent.')
    return redirect('my-offers')


@login_required
@require_POST
def submit_payment(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, buyer=request.user, status='accepted')
    method = request.POST.get('method', 'bkash')
    trx_id = request.POST.get('trx_id', '').strip()
    if not trx_id:
        messages.error(request, 'Transaction ID is required.')
        return redirect('my-offers')

    Payment.objects.update_or_create(
        offer=offer,
        defaults={'buyer': request.user, 'amount': offer.amount,
                  'method': method, 'trx_id': trx_id, 'status': 'pending'}
    )
    notify(offer.listing.seller, request.user, 'payment',
           f'{request.user.username} submitted a {method} payment for "{offer.listing.title}". Please verify.',
           f'/offers/')
    messages.success(request, 'Payment submitted! The seller will verify it.')
    return redirect('my-offers')


@login_required
@require_POST
def confirm_payment(request, offer_id):
    offer   = get_object_or_404(Offer, pk=offer_id, listing__seller=request.user)
    payment = get_object_or_404(Payment, offer=offer)
    payment.status = 'confirmed'
    payment.save()
    offer.listing.status = 'sold'
    offer.listing.save()
    notify(offer.buyer, request.user, 'payment',
           f'Payment confirmed for "{offer.listing.title}". Sale complete! 🎉',
           f'/offers/')
    messages.success(request, 'Payment confirmed and listing marked as sold.')
    return redirect('my-offers')
