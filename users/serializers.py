import typing

from rest_framework import serializers

from chat.models import ChatParticipant
from course.models import Course

from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, help_text='User password')
    course_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Course.objects.all(), source='courses', write_only=True, required=False
    )
    courses = serializers.StringRelatedField(many=True, read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'is_active',
            'password',
            'course_ids',
            'courses',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def _set_courses_and_chat(self, user: User, courses: list[Course]) -> None:
        user.courses.set(courses)
        for course in courses:
            if course.chat:
                ChatParticipant.objects.get_or_create(chat=course.chat, user=user)

    def create(self, validated_data: dict[str, typing.Any]) -> User:
        courses = validated_data.pop('courses', [])
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        if courses:
            self._set_courses_and_chat(user, courses)
        return user

    def update(self, instance: User, validated_data: dict[str, typing.Any]) -> User:
        courses = validated_data.pop('courses', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if courses is not None:
            self._set_courses_and_chat(instance, courses)
        return instance
