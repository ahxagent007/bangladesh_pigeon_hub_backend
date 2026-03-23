from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Listing, SavedListing
from .forms import ListingForm
from apps.pigeons.models import Breed

def listing_list(request):
    qs = Listing.objects.filter(status='active').select_related(
        'pigeon__breed', 'seller', 'pigeon'
    ).prefetch_related('pigeon__images')

    # Filters
    breed = request.GET.get('breed')
    min_p = request.GET.get('min_price')
    max_p = request.GET.get('max_price')
    location = request.GET.get('location')
    q = request.GET.get('q')

    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(pigeon__name__icontains=q) |
            Q(pigeon__breed__name__icontains=q)
        )
    if breed:
        qs = qs.filter(pigeon__breed__id=breed)
    if min_p:
        qs = qs.filter(price__gte=min_p)
    if max_p:
        qs = qs.filter(price__lte=max_p)
    if location:
        qs = qs.filter(location__icontains=location)

    breeds = Breed.objects.all()
    return render(request, 'marketplace/listing_list.html', {
        'listings': qs,
        'breeds': breeds,
        'current_filters': request.GET,
    })

def listing_detail(request, pk):
    listing = get_object_or_404(
        Listing.objects.select_related('pigeon__breed', 'seller')
                       .prefetch_related('pigeon__images'),
        pk=pk, status='active'
    )
    listing.increment_views()
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedListing.objects.filter(
            user=request.user, listing=listing
        ).exists()
    return render(request, 'marketplace/listing_detail.html', {
        'listing': listing,
        'is_saved': is_saved,
    })

@login_required
def add_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, user=request.user)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            # Mark pigeon as for sale
            listing.pigeon.is_for_sale = True
            listing.pigeon.save()
            messages.success(request, 'Listing created!')
            return redirect('listing-detail', pk=listing.pk)
    else:
        form = ListingForm(user=request.user)
    return render(request, 'marketplace/add_listing.html', {'form': form})

@login_required
def my_listings(request):
    listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_listings.html', {'listings': listings})

@login_required
def toggle_save(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    obj, created = SavedListing.objects.get_or_create(
        user=request.user, listing=listing
    )
    if not created:
        obj.delete()
    return redirect('listing-detail', pk=pk)