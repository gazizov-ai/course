import typing

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Chat, ChatParticipant, Message
from .services import create_chat

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class ChatParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    chat_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ChatParticipant
        fields = ['id', 'user', 'joined_at', 'user_id', 'chat_id']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']


class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'name', 'is_group', 'created_at', 'participants', 'messages']


class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class EmptySerializer(serializers.Serializer):
    pass

class CreateChatSerializer(serializers.ModelSerializer):
    user_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'name', 'is_group', 'user_ids']

    def create(self, validated_data: dict[str, typing.Any]) -> Chat:
        user_ids = validated_data.pop('user_ids')
        return create_chat(validated_data['name'], validated_data['is_group'], user_ids)

    def update(self, instance: Chat, validated_data: dict[str, typing.Any]) -> Chat:
        user_ids = validated_data.pop('user_ids', [])
        instance.name = validated_data.get('name', instance.name)
        instance.is_group = validated_data.get('is_group', instance.is_group)
        instance.save()

        ChatParticipant.objects.filter(chat=instance).delete()
        ChatParticipant.objects.bulk_create([ChatParticipant(chat=instance, user_id=uid) for uid in user_ids])

        return instance

class ChatParticipantSerializer(serializers.ModelSerializer):
    user = ChatUserSerializer(read_only=True)

    class Meta:
        model = ChatParticipant
        fields = ['user', 'joined_at']


class ChatSerializer(serializers.ModelSerializer):
    participants = ChatParticipantSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'name', 'is_group', 'created_at', 'participants', 'messages']