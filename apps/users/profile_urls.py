from django.urls import path
from . import profile_views

urlpatterns = [
    path('<str:username>/',        profile_views.public_profile, name='public-profile'),
    path('<str:username>/follow/', profile_views.toggle_follow,  name='toggle-follow'),
]
