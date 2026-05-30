from django.urls import path
from . import views

urlpatterns = [
    path('',                       views.auction_list,      name='auction-list'),
    path('create/',                views.create_auction,    name='auction-create'),
    path('mine/',                  views.my_auctions,       name='my-auctions'),
    path('<int:pk>/',              views.auction_detail,    name='auction-detail'),
    path('<int:pk>/bid/',          views.place_bid,         name='auction-bid'),
    path('<int:pk>/poll/',         views.auction_poll,      name='auction-poll'),
    path('<int:pk>/watch/',        views.toggle_watch,      name='auction-watch'),
    path('<int:pk>/dashboard/',    views.auction_dashboard, name='auction-dashboard'),
]
