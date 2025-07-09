import typing

from rest_framework import serializers

from chat.models import Chat, ChatParticipant

from .models import Course, Module


class UpdateCourseUsersSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(), help_text='Список ID пользователей, которых нужно добавить в курс'
    )


class ModuleSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Module
        fields = ['id', 'course', 'avatar', 'title', 'content', 'order']
        read_only_fields = ['id']


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    users = serializers.StringRelatedField(many=True, read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'avatar',
            'created_at',
            'modules',
            'end_datetime',
            'duration_days',
            'users',
        ]
        read_only_fields = ['id', 'created_at', 'end_datetime']

    def create(self, validated_data: dict[str, typing.Any]) -> Course:
        users_data = validated_data.pop('users', [])
        course = Course.objects.create(**validated_data)

        chat = Chat.objects.create(name=course.title, is_group=True)
        course.chat = chat
        course.save()

        if users_data:
            course.users.set(users_data)
            ChatParticipant.objects.bulk_create([ChatParticipant(chat=chat, user=user) for user in users_data])

        return course
