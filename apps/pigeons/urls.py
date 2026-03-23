from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('pigeons/', views.pigeon_list_view, name='pigeon-list'),
    path('pigeons/<int:pk>/', views.pigeon_detail_view, name='pigeon-detail'),
    path('pigeons/add/', views.add_pigeon_view, name='add-pigeon'),
    path('pigeons/<int:pk>/edit/', views.edit_pigeon_view, name='edit-pigeon'),
    path('pigeons/<int:pk>/delete/', views.delete_pigeon_view, name='delete-pigeon'),
]