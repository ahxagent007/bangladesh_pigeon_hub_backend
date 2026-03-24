from django.urls import path
from apps.users import views

urlpatterns = [
    path('',         views.dashboard_view,    name='dashboard'),
    path('profile/', views.profile_edit_view, name='profile-edit'),
    path('pigeons/', views.my_pigeons_view,   name='my-pigeons'),
]