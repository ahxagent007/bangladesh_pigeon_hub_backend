from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.pigeons.api_views import SiteStatsView

urlpatterns = [
    path('stats/',        SiteStatsView.as_view(),           name='api-stats'),
    path('auth/login/',   TokenObtainPairView.as_view(),  name='api-login'),
    path('auth/refresh/', TokenRefreshView.as_view(),      name='api-token-refresh'),
    path('auth/',         include('apps.users.api_urls')),
    path('users/',        include('apps.users.profile_api_urls')),
    path('pigeons/',      include('apps.pigeons.api_urls')),
    path('marketplace/',  include('apps.marketplace.api_urls')),
    path('pedigree/',     include('apps.pedigrees.api_urls')),
    path('feed/',         include('apps.feed_generator.api_urls')),
    path('messages/',      include('apps.messaging.api_urls')),
    path('auctions/',      include('apps.auctions.api_urls')),
    path('wall/',          include('apps.wall.api_urls')),
    path('notifications/', include('apps.notifications.api_urls')),
]