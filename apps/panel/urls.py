from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.dashboard,       name='panel-dashboard'),
    path('users/',                        views.users,           name='panel-users'),
    path('users/<int:user_id>/',          views.user_detail,     name='panel-user-detail'),
    path('users/<int:user_id>/toggle/',   views.toggle_user,     name='panel-toggle-user'),
    path('listings/',                     views.listings,        name='panel-listings'),
    path('listings/<int:pk>/status/',     views.listing_status,  name='panel-listing-status'),
    path('listings/<int:pk>/delete/',     views.listing_delete,  name='panel-listing-delete'),
    path('auctions/',                     views.auctions,        name='panel-auctions'),
    path('auctions/<int:pk>/cancel/',     views.auction_cancel,  name='panel-auction-cancel'),
    path('offers/',                       views.offers,          name='panel-offers'),
    path('payments/',                     views.payments,        name='panel-payments'),
    path('payments/<int:pk>/action/',     views.payment_action,  name='panel-payment-action'),
    path('wall/',                         views.wall_posts,      name='panel-wall'),
    path('wall/<int:pk>/delete/',         views.wall_delete,     name='panel-wall-delete'),
    path('notifications/',                views.notifications,   name='panel-notifications'),
]
