from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Web pages ──
    path('',            include('apps.pigeons.urls')),
    path('auth/',       include('apps.users.urls')),
    path('dashboard/',  include('apps.users.dashboard_urls')),
    path('marketplace/', include('apps.marketplace.urls')),
    path('pedigree/',   include('apps.pedigrees.urls')),
    path('feed/',       include('apps.feed_generator.urls')),
    path('messages/',   include('apps.messaging.urls')),
    path('offers/',     include('apps.marketplace.offer_urls')),
    path('wall/',          include('apps.wall.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('contests/',      include('apps.contests.urls')),
    path('users/',         include('apps.users.profile_urls')),
    path('auctions/',      include('apps.auctions.urls')),
    path('panel/',         include('apps.panel.urls')),
    path('app/',           include('apps.appconfig.urls')),
    path('legal/',         include('apps.legal.urls')),

    # ── REST API ──
    path('api/',        include('apps.api_urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)