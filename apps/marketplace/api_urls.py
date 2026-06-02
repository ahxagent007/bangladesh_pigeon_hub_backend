from django.urls import path
from . import api_views

urlpatterns = [
    path('',                              api_views.ListingListCreateView.as_view(), name='api-listings'),
    path('mine/',                         api_views.MyListingsView.as_view(),        name='api-my-listings'),
    path('saved/',                        api_views.SavedListingsView.as_view(),     name='api-saved-listings'),
    path('districts/',                    api_views.DistrictListView.as_view(),      name='api-districts'),
    path('offers/',                       api_views.MyOffersView.as_view(),          name='api-my-offers'),
    path('offers/<int:offer_id>/respond/',api_views.RespondOfferView.as_view(),      name='api-respond-offer'),
    path('offers/<int:offer_id>/pay/',    api_views.SubmitPaymentView.as_view(),     name='api-submit-payment'),
    path('<int:pk>/',                     api_views.ListingDetailView.as_view(),     name='api-listing-detail'),
    path('<int:pk>/save/',                api_views.ToggleSaveView.as_view(),        name='api-toggle-save'),
    path('<int:pk>/offer/',               api_views.MakeOfferView.as_view(),         name='api-make-offer'),
]