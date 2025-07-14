from django.urls import path
from rest_framework.routers import DefaultRouter
from education_app.views.chat import ChatViewSet, MessageCreateView

router = DefaultRouter()
router.register(r'chats', ChatViewSet, basename='chat')

urlpatterns = [
    path('chats/<int:chat_id>/messages/', MessageCreateView.as_view(), name='message-create'),
]

urlpatterns += router.urls
