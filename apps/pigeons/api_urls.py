from django.urls import path
from . import api_views

urlpatterns = [
    path('',          api_views.PigeonListCreateView.as_view(), name='api-pigeons'),
    path('<int:pk>/', api_views.PigeonDetailView.as_view(),     name='api-pigeon-detail'),
    path('breeds/',   api_views.BreedListView.as_view(),        name='api-breeds'),
]