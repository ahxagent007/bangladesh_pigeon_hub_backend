from django.urls import path
from . import api_views

urlpatterns = [
    path('',          api_views.PigeonListCreateView.as_view(), name='api-pigeons'),
    path('breeds/',   api_views.BreedListView.as_view(),        name='api-breeds'),
    path('<int:pk>/', api_views.PigeonDetailView.as_view(),     name='api-pigeon-detail'),
    path('<int:pk>/images/',                api_views.PigeonImageUploadView.as_view(), name='api-pigeon-images'),
    path('<int:pk>/images/<int:image_id>/', api_views.PigeonImageDeleteView.as_view(), name='api-pigeon-image-delete'),
]