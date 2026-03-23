from django.urls import path
from . import views

urlpatterns = [
    path('',         views.listing_list,   name='listing-list'),
    path('<int:pk>/', views.listing_detail, name='listing-detail'),
    path('add/',      views.add_listing,    name='add-listing'),
    path('mine/',     views.my_listings,    name='my-listings'),
    path('<int:pk>/save/', views.toggle_save, name='toggle-save'),
]