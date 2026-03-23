from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed_generator_view, name='feed-generator'),
]