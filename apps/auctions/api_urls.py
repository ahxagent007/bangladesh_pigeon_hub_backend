from django.urls import path
from . import api_views

urlpatterns = [
    path('',            api_views.AuctionListView.as_view(),  name='api-auctions'),
    path('<int:pk>/',   api_views.AuctionDetailView.as_view(),name='api-auction-detail'),
    path('<int:pk>/bid/', api_views.PlaceBidView.as_view(),   name='api-auction-bid'),
    path('<int:pk>/poll/', api_views.AuctionPollView.as_view(),name='api-auction-poll'),
]
