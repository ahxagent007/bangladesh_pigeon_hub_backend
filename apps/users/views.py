from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import UpdateView
from .forms import RegisterForm, ProfileForm
from .models import User
from apps.pigeons.models import Pigeon
from apps.marketplace.models import Listing
from apps.messaging.models import Conversation

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def dashboard_view(request):
    pigeons = Pigeon.objects.filter(owner=request.user).count()
    listings = Listing.objects.filter(seller=request.user, status='active').count()
    conversations = Conversation.objects.filter(
        participants=request.user
    ).order_by('-updated_at')[:5]
    unread_count = request.user.sent_messages.filter(is_read=False).count()
    return render(request, 'users/dashboard.html', {
        'pigeon_count': pigeons,
        'listing_count': listings,
        'recent_conversations': conversations,
        'unread_count': unread_count,
    })

@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})