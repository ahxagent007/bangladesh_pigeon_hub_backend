from django.urls import path
from . import views

urlpatterns = [
    path('',                          views.wall_feed,     name='wall-feed'),
    path('post/',                     views.create_post,   name='wall-create-post'),
    path('post/<int:post_id>/like/',  views.toggle_like,   name='wall-toggle-like'),
    path('post/<int:post_id>/comment/', views.add_comment, name='wall-add-comment'),
    path('post/<int:post_id>/delete/', views.delete_post,  name='wall-delete-post'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='wall-delete-comment'),
]
