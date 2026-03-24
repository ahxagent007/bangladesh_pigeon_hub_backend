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

    # ── REST API ──
    path('api/',        include('apps.api_urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)