from django.urls import path

from . import views

urlpatterns = [
    path('chats/', views.ChatListCreateView.as_view(), name='chat-list-create'),
    path('chats/<int:pk>/', views.ChatDetailView.as_view(), name='chat-detail'),
    path(
        'chats/<int:chat_id>/<int:user_id>/add-participant/', views.AddParticipantView.as_view(), name='add-participant'
    ),
    path(
        'chats/<int:chat_id>/<int:user_id>/remove-participant/',
        views.RemoveParticipantView.as_view(),
        name='remove-participant',
    ),
    path('messages/<int:chat_id>/', views.MessageCreateView.as_view(), name='message-create'),
]
