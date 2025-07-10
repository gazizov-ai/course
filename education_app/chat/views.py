from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from .models import Chat, ChatParticipant
from .serializers import CreateChatSerializer, ChatSerializer,MessageSerializer
from .serializers import ChatParticipantSerializer

User = get_user_model()


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all().prefetch_related('participants', 'messages')

    def get_permissions(self):
        if self.action in ['create', 'add_participant', 'remove_participant']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateChatSerializer
        return ChatSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Chat.objects.all().prefetch_related('participants', 'messages')
        return Chat.objects.filter(participants__user=user).prefetch_related('participants', 'messages')

    @action(detail=True, methods=['post'], url_path='add-participant')
    def add_participant(self, request: Request, pk: int) -> Response:
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)

        try:
            chat = Chat.objects.get(pk=pk)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=404)

        if ChatParticipant.objects.filter(chat=chat, user_id=user_id).exists():
            return Response({'error': 'User is already a participant'}, status=400)

        participant = ChatParticipant.objects.create(chat=chat, user_id=user_id)
        serializer = ChatParticipantSerializer(participant)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['post'], url_path='remove-participant')
    def remove_participant(self, request: Request, pk: int) -> Response:
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)

        try:
            participant = ChatParticipant.objects.get(chat_id=pk, user_id=user_id)
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
