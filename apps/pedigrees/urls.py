from django.urls import path
from . import views

urlpatterns = [
    path('',                       views.pedigree_index,  name='pedigree-index'),
    path('<int:pigeon_id>/',        views.pedigree_view,   name='pedigree-view'),
    path('<int:pigeon_id>/edit/',   views.pedigree_edit,   name='pedigree-edit'),
]