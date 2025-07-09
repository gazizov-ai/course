from django.contrib.auth import get_user_model
from rest_framework import generics, serializers
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from .models import Chat, ChatParticipant, Message
from .serializers import CreateChatSerializer, ChatSerializer, EmptySerializer,MessageSerializer

User = get_user_model()


class ChatListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Chat.objects.all().prefetch_related('participants', 'messages')
        return Chat.objects.filter(participants__user=user).prefetch_related('participants', 'messages')

    def get_serializer_class(self) -> type[serializers.ModelSerializer]:
        if self.request.method == 'POST':
            return CreateChatSerializer
        return ChatSerializer


class ChatDetailView(generics.RetrieveAPIView):
    queryset = Chat.objects.all().prefetch_related('participants', 'messages')
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]


class AddParticipantView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = EmptySerializer

    def post(self, request: Request, chat_id: int, user_id: int) -> Response:
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)

        try:
            chat = Chat.objects.get(pk=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=404)

        if ChatParticipant.objects.filter(chat=chat, user_id=user_id).exists():
            return Response({'error': 'User is already a participant'}, status=400)

        participant = ChatParticipant.objects.create(chat=chat, user_id=user_id)
        from .serializers import ChatParticipantSerializer

        serializer = ChatParticipantSerializer(participant)
        return Response(serializer.data, status=201)


class RemoveParticipantView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = EmptySerializer

    def post(self, request: Request, chat_id: int, user_id: int) -> Response:
        try:
            participant = ChatParticipant.objects.get(chat_id=chat_id, user_id=user_id)
            participant.delete()
            return Response({'status': 'participant removed'})
        except ChatParticipant.DoesNotExist:
            return Response({'error': 'Participant not found'}, status=404)


class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: BaseSerializer) -> None:
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)
        serializer.save(sender=self.request.user, chat=chat)
