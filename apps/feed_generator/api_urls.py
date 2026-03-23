from django.urls import path
from . import api_views

urlpatterns = [
    path('generate/', api_views.FeedGenerateView.as_view(), name='api-feed-generate'),
]