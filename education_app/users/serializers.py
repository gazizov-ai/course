import typing

from rest_framework import serializers

from education_app.course.models import Course
from .models import User
from .services import create_user, update_user, set_courses_and_chats


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
        if courses:
            set_courses_and_chats(user, courses)

    def create(self, validated_data: dict[str, typing.Any]) -> User:
        return create_user(validated_data)

    def update(self, instance: User, validated_data: dict[str, typing.Any]) -> User:
        return update_user(instance, validated_data)
