from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Event, BD_DISTRICTS


def event_list(request):
    today  = timezone.now().date()
    upcoming = Event.objects.filter(date__gte=today).order_by('date')
    past     = Event.objects.filter(date__lt=today).order_by('-date')[:10]
    return render(request, 'events/list.html', {
        'upcoming': upcoming, 'past': past, 'districts': BD_DISTRICTS,
        'selected_district': request.GET.get('district', ''),
        'selected_type': request.GET.get('type', ''),
    })


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/detail.html', {'event': event})


@login_required
def create_event(request):
    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        event_type  = request.POST.get('event_type', 'other')
        location    = request.POST.get('location', '').strip()
        district    = request.POST.get('district', 'other')
        date        = request.POST.get('date')
        time        = request.POST.get('time') or None
        image       = request.FILES.get('image')

        if not all([title, description, location, date]):
            messages.error(request, 'Please fill in all required fields.')
        else:
            event = Event.objects.create(
                organizer=request.user, title=title, description=description,
                event_type=event_type, location=location, district=district,
                date=date, time=time, image=image
            )
            messages.success(request, 'Event created!')
            return redirect('event-detail', pk=event.pk)

    return render(request, 'events/create.html', {
        'event_types': Event.TYPES,
        'districts': BD_DISTRICTS,
    })
