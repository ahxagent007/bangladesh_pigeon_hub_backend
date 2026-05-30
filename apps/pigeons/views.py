from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch
from .models import Pigeon, PigeonImage, Breed
from .forms import PigeonForm, PigeonImageForm

def home_view(request):
    featured = (
        Pigeon.objects.filter(is_for_sale=True)
        .select_related('breed')
        .prefetch_related('images')
        .order_by('-created_at')[:8]
    )
    breeds = Breed.objects.all()

    from apps.wall.models import Post, Like
    recent_posts = (
        Post.objects
        .select_related('author', 'pigeon__breed')
        .prefetch_related('images', 'likes', 'comments')
        .order_by('-created_at')[:6]
    )
    liked_post_ids = set()
    if request.user.is_authenticated:
        liked_post_ids = set(
            Like.objects.filter(user=request.user).values_list('post_id', flat=True)
        )

    from django.utils import timezone
    from apps.auctions.models import Auction
    now = timezone.now()
    # Auto-activate upcoming auctions that have started
    Auction.objects.filter(status='upcoming', start_time__lte=now).update(status='live')

    live_auctions = (
        Auction.objects.filter(status='live')
        .select_related('seller', 'pigeon__breed')
        .prefetch_related('gallery', 'pigeon__images')
        .order_by('end_time')[:6]
    )
    upcoming_auctions = (
        Auction.objects.filter(status='upcoming')
        .select_related('seller', 'pigeon__breed')
        .prefetch_related('gallery', 'pigeon__images')
        .order_by('start_time')[:4]
    )

    return render(request, 'pigeons/home.html', {
        'featured':          featured,
        'breeds':            breeds,
        'recent_posts':      recent_posts,
        'liked_post_ids':    liked_post_ids,
        'live_auctions':     live_auctions,
        'upcoming_auctions': upcoming_auctions,
    })

@login_required
def pigeon_list_view(request):
    pigeons = Pigeon.objects.filter(
        owner=request.user
    ).select_related('breed').prefetch_related('images').order_by('-created_at')
    return render(request, 'pigeons/pigeon_list.html', {'pigeons': pigeons})

def pigeon_detail_view(request, pk):
    pigeon = get_object_or_404(
        Pigeon.objects.select_related('breed', 'owner').prefetch_related('images'),
        pk=pk
    )
    return render(request, 'pigeons/pigeon_detail.html', {'pigeon': pigeon})

@login_required
def add_pigeon_view(request):
    if request.method == 'POST':
        form = PigeonForm(request.POST)
        image_form = PigeonImageForm(request.POST, request.FILES)
        if form.is_valid():
            pigeon = form.save(commit=False)
            pigeon.owner = request.user
            pigeon.save()
            if request.FILES.get('image'):
                PigeonImage.objects.create(
                    pigeon=pigeon,
                    image=request.FILES['image'],
                    is_primary=True
                )
            messages.success(request, f'"{pigeon.name}" added successfully!')
            return redirect('pigeon-detail', pk=pigeon.pk)
    else:
        form = PigeonForm()
        image_form = PigeonImageForm()
    return render(request, 'pigeons/add_pigeon.html', {
        'form': form,
        'image_form': image_form,
    })

@login_required
def edit_pigeon_view(request, pk):
    pigeon = get_object_or_404(Pigeon, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PigeonForm(request.POST, instance=pigeon)
        if form.is_valid():
            form.save()
            if request.FILES.get('image'):
                PigeonImage.objects.filter(pigeon=pigeon, is_primary=True).delete()
                PigeonImage.objects.create(
                    pigeon=pigeon,
                    image=request.FILES['image'],
                    is_primary=True
                )
            messages.success(request, 'Pigeon updated!')
            return redirect('pigeon-detail', pk=pigeon.pk)
    else:
        form = PigeonForm(instance=pigeon)
    return render(request, 'pigeons/add_pigeon.html', {
        'form': form,
        'image_form': PigeonImageForm(),
        'pigeon': pigeon,
        'editing': True,
    })

@login_required
def delete_pigeon_view(request, pk):
    pigeon = get_object_or_404(Pigeon, pk=pk, owner=request.user)
    if request.method == 'POST':
        name = pigeon.name
        pigeon.delete()
        messages.success(request, f'"{name}" deleted.')
        return redirect('pigeon-list')
    return render(request, 'pigeons/confirm_delete.html', {'pigeon': pigeon})