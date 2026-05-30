from django.shortcuts import render
from django.db.models import Avg, Min, Max, Count
from django.utils import timezone
from datetime import timedelta
from .models import Listing, BD_DISTRICTS
from apps.pigeons.models import Breed


def insights(request):
    today      = timezone.now().date()
    last_30    = today - timedelta(days=30)
    prev_30    = today - timedelta(days=60)

    # Price by breed
    by_breed = (
        Listing.objects
        .filter(status__in=['active','sold'])
        .values('pigeon__breed__name')
        .annotate(avg=Avg('price'), mn=Min('price'), mx=Max('price'), cnt=Count('id'))
        .exclude(pigeon__breed__name=None)
        .order_by('-cnt')[:15]
    )

    # Listings by district
    by_district = (
        Listing.objects.filter(status='active')
        .values('district')
        .annotate(cnt=Count('id'))
        .order_by('-cnt')
    )
    district_map = dict(BD_DISTRICTS)
    for row in by_district:
        row['label'] = district_map.get(row['district'], row['district'])

    max_district = max((r['cnt'] for r in by_district), default=1)

    # Recent trend
    recent_listings   = Listing.objects.filter(created_at__date__gte=last_30).count()
    previous_listings = Listing.objects.filter(created_at__date__gte=prev_30, created_at__date__lt=last_30).count()
    trend = recent_listings - previous_listings

    # Overall stats
    total    = Listing.objects.count()
    active   = Listing.objects.filter(status='active').count()
    sold     = Listing.objects.filter(status='sold').count()
    avg_all  = Listing.objects.aggregate(avg=Avg('price'))['avg'] or 0

    return render(request, 'marketplace/insights.html', {
        'by_breed': by_breed,
        'by_district': by_district,
        'max_district': max_district,
        'recent_listings': recent_listings,
        'previous_listings': previous_listings,
        'trend': trend,
        'total': total,
        'active': active,
        'sold': sold,
        'avg_all': round(avg_all),
    })
