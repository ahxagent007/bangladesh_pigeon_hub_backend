from django.urls import path
from . import api_views

urlpatterns = [
    path('',                          api_views.WallPostListView.as_view(),    name='api-wall'),
    path('create/',                   api_views.CreatePostView.as_view(),      name='api-wall-create'),
    path('<int:post_id>/like/',       api_views.ToggleLikeView.as_view(),      name='api-wall-like'),
    path('<int:post_id>/comments/',   api_views.CommentListCreateView.as_view(), name='api-wall-comments'),
    path('comment/<int:comment_id>/delete/', api_views.CommentDeleteView.as_view(), name='api-wall-comment-delete'),
]
