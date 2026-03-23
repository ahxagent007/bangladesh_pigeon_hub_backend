from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('auth/login/',   TokenObtainPairView.as_view(),  name='api-login'),
    path('auth/refresh/', TokenRefreshView.as_view(),      name='api-token-refresh'),
    path('auth/',         include('apps.users.api_urls')),
    path('pigeons/',      include('apps.pigeons.api_urls')),
    path('marketplace/',  include('apps.marketplace.api_urls')),
    path('pedigree/',     include('apps.pedigrees.api_urls')),
    path('feed/',         include('apps.feed_generator.api_urls')),
    path('messages/',     include('apps.messaging.api_urls')),
]