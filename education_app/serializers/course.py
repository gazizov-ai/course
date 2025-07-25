import typing

from rest_framework import serializers

from education_app.models.course import Course, Module, Lesson, Question, Answer, Tag
from education_app.services.course import CourseService


class UpdateCourseUsersSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='Список ID пользователей, которых нужно добавить в курс',
    )


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'
        read_only_fields = ['id']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields= '__all__'
        read_only_fields = ['id']


class QuestionShortSerializer(serializers.ModelSerializer):
    answer_ids = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields= ('id', 'title', 'content', 'answer_ids')
        read_only_fields = ['id']


class LessonSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['id']


class LessonShortSerializer(serializers.ModelSerializer):
    # question_ids = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='questions')
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Lesson
        fields = ('id', 'module', 'avatar', 'title', 'type')
        read_only_fields = ['id']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Module
        fields = ('id', 'course', 'avatar', 'title', 'content', 'order', 'lessons')
        read_only_fields = ['id']


class ModuleShortSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)
    lesson_ids = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='lessons')

    class Meta:
        model = Module
        fields = ('id', 'course', 'avatar', 'title', 'order', 'lesson_ids')
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['id']


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    users = serializers.StringRelatedField(many=True, read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'tags',
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
        return CourseService.create_course_with_users_and_chat(validated_data)
