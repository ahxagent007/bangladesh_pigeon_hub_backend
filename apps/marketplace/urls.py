from django.urls import path
from . import views, offer_views, review_views
from .insights_views import insights

urlpatterns = [
    path('',                         views.listing_list,                name='listing-list'),
    path('add/',                     views.add_listing,                 name='add-listing'),
    path('mine/',                    views.my_listings,                 name='my-listings'),
    path('insights/',                insights,                          name='market-insights'),
    path('<int:pk>/',                views.listing_detail,              name='listing-detail'),
    path('<int:pk>/save/',           views.toggle_save,                 name='toggle-save'),
    path('<int:listing_id>/offer/',  offer_views.make_offer,            name='make-offer'),
    path('offers/',                  offer_views.my_offers,             name='my-offers'),
    path('offers/<int:offer_id>/respond/', offer_views.respond_offer,  name='respond-offer'),
    path('offers/<int:offer_id>/pay/',     offer_views.submit_payment,  name='submit-payment'),
    path('offers/<int:offer_id>/confirm/', offer_views.confirm_payment, name='confirm-payment'),
]

# Review URLs wired via users/profile_urls but need path here too
from django.urls import path as _p
urlpatterns += [
    _p('review/<str:username>/', review_views.leave_review, name='leave-review'),
]