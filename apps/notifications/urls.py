from django.urls import path
from . import views

urlpatterns = [
    path('',          views.notification_list, name='notifications'),
    path('read-all/', views.mark_all_read,     name='notifications-read-all'),
    path('count/',    views.unread_count,       name='notifications-count'),
]
