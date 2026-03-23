from django.shortcuts import render
from .logic import generate_feed, PURPOSE_TARGETS


PURPOSE_LABELS = {
    'racing':      '🏆 Racing',
    'breeding':    '🥚 Breeding',
    'molting':     '🔄 Molting',
    'maintenance': '⚖️ Maintenance',
    'young':       '🐣 Young Pigeons',
}


def feed_generator_view(request):
    result = None
    selected_purpose = 'maintenance'

    if request.method == 'POST' or request.GET.get('purpose'):
        selected_purpose = (
            request.POST.get('purpose') or
            request.GET.get('purpose', 'maintenance')
        )
        target_protein = (
            request.POST.get('target_protein') or
            request.GET.get('target_protein')
        )
        result = generate_feed(selected_purpose, target_protein)

    # Build a list of (value, label) tuples instead of a dict
    purpose_choices = [
        (key, PURPOSE_LABELS.get(key, key.capitalize()))
        for key in PURPOSE_TARGETS.keys()
    ]

    return render(request, 'feed_generator/generator.html', {
        'result':           result,
        'purpose_choices':  purpose_choices,
        'selected_purpose': selected_purpose,
        'target_protein':   request.POST.get('target_protein', ''),
    })