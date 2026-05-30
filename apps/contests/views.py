from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Contest, ContestEntry, ContestVote
from apps.pigeons.models import Pigeon
from apps.notifications.models import notify


def contest_list(request):
    today    = timezone.now().date()
    active   = Contest.objects.filter(is_active=True, voting_end_date__gte=today)
    past     = Contest.objects.filter(voting_end_date__lt=today).order_by('-end_date')[:6]
    return render(request, 'contests/list.html', {'active': active, 'past': past})


def contest_detail(request, pk):
    contest = get_object_or_404(Contest, pk=pk)
    entries = contest.entries.select_related('user').order_by('-votes__id')
    today   = timezone.now().date()
    can_enter  = request.user.is_authenticated and today <= contest.end_date
    can_vote   = request.user.is_authenticated and contest.end_date < today <= contest.voting_end_date
    user_entry = None
    user_vote  = None
    if request.user.is_authenticated:
        user_entry = ContestEntry.objects.filter(contest=contest, user=request.user).first()
        user_vote  = ContestVote.objects.filter(contest=contest, voter=request.user).first()

    entries_with_counts = [(e, e.vote_count) for e in entries]
    entries_with_counts.sort(key=lambda x: x[1], reverse=True)

    return render(request, 'contests/detail.html', {
        'contest': contest,
        'entries_with_counts': entries_with_counts,
        'can_enter': can_enter,
        'can_vote': can_vote,
        'user_entry': user_entry,
        'user_vote': user_vote,
        'today': today,
    })


@login_required
def submit_entry(request, pk):
    contest = get_object_or_404(Contest, pk=pk, is_active=True)
    today   = timezone.now().date()
    if today > contest.end_date:
        messages.error(request, 'Entry period has closed.')
        return redirect('contest-detail', pk=pk)

    if ContestEntry.objects.filter(contest=contest, user=request.user).exists():
        messages.error(request, 'You already entered this contest.')
        return redirect('contest-detail', pk=pk)

    if request.method == 'POST':
        image   = request.FILES.get('image')
        caption = request.POST.get('caption', '').strip()
        pigeon_id = request.POST.get('pigeon_id') or None
        pigeon  = None
        if pigeon_id:
            try:
                pigeon = Pigeon.objects.get(pk=pigeon_id, owner=request.user)
            except Pigeon.DoesNotExist:
                pass
        if not image:
            messages.error(request, 'A photo is required.')
        else:
            ContestEntry.objects.create(contest=contest, user=request.user,
                                        pigeon=pigeon, image=image, caption=caption)
            messages.success(request, 'Entry submitted! Good luck 🐦')
            return redirect('contest-detail', pk=pk)

    user_pigeons = Pigeon.objects.filter(owner=request.user)
    return render(request, 'contests/enter.html', {'contest': contest, 'user_pigeons': user_pigeons})


@login_required
@require_POST
def cast_vote(request, pk):
    contest  = get_object_or_404(Contest, pk=pk)
    entry_id = request.POST.get('entry_id')
    entry    = get_object_or_404(ContestEntry, pk=entry_id, contest=contest)
    today    = timezone.now().date()

    if not (contest.end_date < today <= contest.voting_end_date):
        return JsonResponse({'error': 'Voting is not open.'}, status=400)
    if ContestVote.objects.filter(contest=contest, voter=request.user).exists():
        return JsonResponse({'error': 'Already voted.'}, status=400)

    ContestVote.objects.create(contest=contest, voter=request.user, entry=entry)
    notify(entry.user, request.user, 'like',
           f'{request.user.username} voted for your entry in "{contest.title}"!',
           f'/contests/{pk}/')
    return JsonResponse({'vote_count': entry.vote_count})
