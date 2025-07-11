from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from education_app.models.chat import Chat, ChatParticipant
from education_app.serializers.chat import CreateChatSerializer, ChatSerializer, MessageSerializer, \
    ChatParticipantSerializer
from education_app.services.chat import ChatService

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

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_ids = serializer.validated_data.pop('user_ids')
        name = serializer.validated_data.get('name', '')
        is_group = serializer.validated_data.get('is_group', False)

        chat = ChatService.create_chat(name=name, is_group=is_group, user_ids=user_ids)
        return Response(ChatSerializer(chat).data, status=201)

    def update(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_ids = serializer.validated_data.pop('user_ids', [])
        name = serializer.validated_data.get('name', instance.name)
        is_group = serializer.validated_data.get('is_group', instance.is_group)

        chat = ChatService.update_chat(instance, name, is_group, user_ids)
        return Response(ChatSerializer(chat).data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='user_id', required=True, type=int,
                location=OpenApiParameter.QUERY,
                description='ID пользователя для добавления в чат'
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='add-participant')
    def add_participant(self, request: Request, pk: int) -> Response:
        user_id = request.query_params.get('user_id')
        if not user_id:
            raise ValidationError({'user_id': 'Параметр обязателен'})

        try:
            chat = Chat.objects.get(pk=pk)
        except Chat.DoesNotExist:
            raise NotFound('Чат не найден')

        if ChatParticipant.objects.filter(chat=chat, user_id=user_id).exists():
            raise ValidationError({'user_id': 'Пользователь уже участвует в чате'})

        participant = ChatParticipant.objects.create(chat=chat, user_id=user_id)
        participant = ChatParticipant.objects.select_related('user').get(id=participant.id)
        serializer = ChatParticipantSerializer(participant)
        return Response(serializer.data, status=201)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='user_id', required=True, type=int,
                location=OpenApiParameter.QUERY,
                description='ID пользователя для удаления'
            )
        ]
    )
    @action(detail=True, methods=['post'], url_path='remove-participant')
    def remove_participant(self, request: Request, pk: int) -> Response:
        user_id = request.query_params.get('user_id')
        if not user_id:
            raise ValidationError({'user_id': 'Параметр обязателен'})

        try:
            participant = ChatParticipant.objects.get(chat_id=pk, user_id=user_id)
        except ChatParticipant.DoesNotExist:
            raise NotFound('Участник не найден')

        participant.delete()
        return Response({'status': 'Участник удалён'})


class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: BaseSerializer) -> None:
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)
        serializer.save(sender=self.request.user, chat=chat)
