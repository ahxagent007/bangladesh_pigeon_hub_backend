from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.inbox_view,        name='inbox'),
    path('<int:pk>/',               views.conversation_view, name='conversation'),
    path('start/<int:listing_id>/', views.start_conversation, name='start-conversation'),
]