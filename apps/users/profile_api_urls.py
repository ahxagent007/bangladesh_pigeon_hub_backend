from django.urls import path
from . import api_views

urlpatterns = [
    path('<str:username>/follow/',  api_views.ToggleFollowView.as_view(),  name='api-follow'),
    path('<str:username>/reviews/', api_views.UserReviewsView.as_view(),   name='api-user-reviews'),
    path('<str:username>/',         api_views.PublicProfileView.as_view(), name='api-public-profile'),
]
