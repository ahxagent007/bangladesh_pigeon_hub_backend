from django.urls import path
from . import api_views

urlpatterns = [
    path('',                        api_views.WallPostListView.as_view(), name='api-wall'),
    path('<int:post_id>/like/',      api_views.ToggleLikeView.as_view(),  name='api-wall-like'),
]
