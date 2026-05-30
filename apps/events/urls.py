from django.urls import path
from . import views

urlpatterns = [
    path('',            views.event_list,   name='event-list'),
    path('create/',     views.create_event, name='event-create'),
    path('<int:pk>/',   views.event_detail, name='event-detail'),
]
