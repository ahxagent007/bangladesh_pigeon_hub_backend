from django.urls import path
from . import api_views

urlpatterns = [
    path('',       api_views.NotificationListView.as_view(), name='api-notifications'),
    path('count/', api_views.UnreadCountView.as_view(),      name='api-notif-count'),
]
