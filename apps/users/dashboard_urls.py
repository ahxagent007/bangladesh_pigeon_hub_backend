from django.urls import path
from . import views

urlpatterns = [
    path('',        views.dashboard_view,    name='dashboard'),
    path('profile/', views.profile_edit_view, name='profile-edit'),
]