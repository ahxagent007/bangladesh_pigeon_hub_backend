from django.urls import path
from . import api_views

urlpatterns = [
    path('',           api_views.ListingListCreateView.as_view(), name='api-listings'),
    path('<int:pk>/',  api_views.ListingDetailView.as_view(),     name='api-listing-detail'),
]