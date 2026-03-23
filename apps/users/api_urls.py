from django.urls import path
from . import api_views

urlpatterns = [
    path('register/', api_views.RegisterView.as_view(), name='api-register'),
    path('me/',       api_views.MeView.as_view(),       name='api-me'),
]