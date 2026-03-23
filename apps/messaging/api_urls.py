from django.urls import path
from . import api_views

urlpatterns = [
    path('',              api_views.ConversationListView.as_view(), name='api-conversations'),
    path('<int:pk>/',     api_views.ConversationDetailView.as_view(), name='api-conversation'),
    path('<int:pk>/send/', api_views.SendMessageView.as_view(),      name='api-send-message'),
]