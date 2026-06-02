from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Listing, SavedListing
from .forms import ListingDetailsForm, QuickPigeonForm
from apps.pigeons.models import Pigeon, PigeonImage, Breed


def listing_list(request):
    qs = Listing.objects.filter(status='active').select_related(
        'pigeon__breed', 'seller', 'pigeon'
    ).prefetch_related('pigeon__images')

    breed   = request.GET.get('breed')
    min_p   = request.GET.get('min_price')
    max_p   = request.GET.get('max_price')
    location = request.GET.get('location')
    q       = request.GET.get('q')

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
    user_pigeons = (
        Pigeon.objects.filter(owner=request.user)
        .exclude(listing__status='active')
        .select_related('breed')
        .prefetch_related('images')
        .order_by('-created_at')
    )
    breeds = Breed.objects.all().order_by('name')

    listing_form = ListingDetailsForm()
    pigeon_form  = QuickPigeonForm()
    errors = []

    if request.method == 'POST':
        from apps.recaptcha import verify_recaptcha
        if not verify_recaptcha(request.POST.get('g-recaptcha-response')):
            errors.append('Please complete the CAPTCHA verification.')
            return render(request, 'marketplace/add_listing.html', {
                'listing_form': listing_form, 'pigeon_form': pigeon_form,
                'user_pigeons': user_pigeons, 'breeds': breeds, 'errors': errors,
                'post_mode': request.POST.get('mode', 'existing'),
            })
        mode = request.POST.get('mode', 'existing')
        listing_form = ListingDetailsForm(request.POST)

        if mode == 'existing':
            pigeon_id = request.POST.get('pigeon_id')
            if not pigeon_id:
                errors.append('Please select a pigeon from your flock.')
            else:
                pigeon = get_object_or_404(Pigeon, pk=pigeon_id, owner=request.user)
                if listing_form.is_valid():
                    listing = listing_form.save(commit=False)
                    listing.seller = request.user
                    listing.pigeon = pigeon
                    listing.save()
                    pigeon.is_for_sale = True
                    pigeon.save()
                    messages.success(request, f'"{pigeon.name}" is now listed for sale!')
                    return redirect('listing-detail', pk=listing.pk)

        elif mode == 'new':
            pigeon_form = QuickPigeonForm(request.POST, request.FILES)
            if listing_form.is_valid() and pigeon_form.is_valid():
                pigeon = pigeon_form.save(commit=False)
                pigeon.owner = request.user
                pigeon.is_for_sale = True

                pedigree_file = request.FILES.get('pedigree_image_upload')
                if pedigree_file:
                    pigeon.pedigree_image = pedigree_file

                pigeon.save()

                pigeon_photo = request.FILES.get('pigeon_image')
                if pigeon_photo:
                    PigeonImage.objects.create(
                        pigeon=pigeon,
                        image=pigeon_photo,
                        is_primary=True,
                    )

                listing = listing_form.save(commit=False)
                listing.seller = request.user
                listing.pigeon = pigeon
                listing.save()

                messages.success(request, f'"{pigeon.name}" is now listed for sale!')
                return redirect('listing-detail', pk=listing.pk)

    return render(request, 'marketplace/add_listing.html', {
        'listing_form': listing_form,
        'pigeon_form': pigeon_form,
        'user_pigeons': user_pigeons,
        'breeds': breeds,
        'errors': errors,
        'post_mode': request.POST.get('mode', 'existing') if request.method == 'POST' else 'existing',
    })


@login_required
def my_listings(request):
    listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_listing.html', {'listings': listings})


@login_required
def toggle_save(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    obj, created = SavedListing.objects.get_or_create(
        user=request.user, listing=listing
    )
    if not created:
        obj.delete()
    return redirect('listing-detail', pk=pk)
