import typing

from rest_framework import serializers
from education_app.models.course import Course, Module
from education_app.services.course import CourseService


class UpdateCourseUsersSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Список ID пользователей, которых нужно добавить в курс",
    )


class ModuleSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Module
        fields = ("id", "course", "avatar", "title", "content", "order")
        read_only_fields = ["id"]


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    users = serializers.StringRelatedField(many=True, read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "avatar",
            "created_at",
            "modules",
            "end_datetime",
            "duration_days",
            "users",
        ]
        read_only_fields = ["id", "created_at", "end_datetime"]

    def create(self, validated_data: dict[str, typing.Any]) -> Course:
        return CourseService.create_course_with_users_and_chat(validated_data)
