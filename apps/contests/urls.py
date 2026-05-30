from django.urls import path
from . import views

urlpatterns = [
    path('',                   views.contest_list,   name='contest-list'),
    path('<int:pk>/',          views.contest_detail, name='contest-detail'),
    path('<int:pk>/enter/',    views.submit_entry,   name='contest-enter'),
    path('<int:pk>/vote/',     views.cast_vote,      name='contest-vote'),
]
