from django.urls import path
from django.views.generic import RedirectView
from . import offer_views

urlpatterns = [
    path('',                            offer_views.my_offers,       name='my-offers'),
    path('<int:offer_id>/respond/',     offer_views.respond_offer,   name='respond-offer'),
    path('<int:offer_id>/pay/',         offer_views.submit_payment,  name='submit-payment'),
    path('<int:offer_id>/confirm/',     offer_views.confirm_payment, name='confirm-payment'),
    # Legacy notification URLs → redirect to offers dashboard
    path('listing/<int:listing_id>/',   RedirectView.as_view(url='/offers/', permanent=False)),
]
