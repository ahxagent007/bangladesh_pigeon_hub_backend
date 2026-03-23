from django.urls import path
from . import api_views

urlpatterns = [
    path('<int:pigeon_id>/',      api_views.PedigreeView.as_view(),  name='api-pedigree'),
    path('<int:pigeon_id>/edit/', api_views.PedigreeEditView.as_view(), name='api-pedigree-edit'),
]