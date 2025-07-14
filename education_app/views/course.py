from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, JsonResponse
from django.http import JsonResponse as JsonResponseType
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from education_app.tasks import clean_expired_enrollments

from education_app.models.course import Course, Module, Lesson, Question, Answer, Tag
from education_app.serializers.course import CourseSerializer, ModuleSerializer, LessonSerializer, QuestionSerializer, AnswerSerializer, TagSerializer
from education_app.services.course import CourseService


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'user_ids': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                        'example': [1, 2, 3],
                        'description': 'Список ID пользователей, которых нужно добавить в курс',
                    }
                },
                'required': ['user_ids'],
            }
        },
        responses={
            200: OpenApiResponse(
                description='Успешное обновление',
                examples=[
                    OpenApiExample(
                        name='Успешное обновление',
                        value={'detail': 'Course users updated successfully'},
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description='Ошибка: user_ids не список',
                examples=[
                    OpenApiExample(
                        name='Ошибка: user_ids не список',
                        value={'detail': 'user_ids must be a list'},
                        response_only=True,
                    )
                ],
            ),
        },
        description='Обновляет состав участников курса. Все, кто не указан в user_ids, будут удалены.',
        examples=[OpenApiExample('Пример запроса', value={'user_ids': [1, 2, 3]}, request_only=True)],
    )
    @action(detail=True, methods=['post'], url_path='update_users')
    def update_course_users(self, request: Request, pk: int | None = None) -> Response:
        course = self.get_object()
        user_ids = request.data.get('user_ids', [])

        CourseService.update_course_users(course, user_ids)

        return Response({'status': 'users updated successfully'})


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@user_passes_test(lambda u: u.is_staff)
def run_cleanup_view(request: HttpRequest, course_id: int) -> JsonResponseType:
    course = get_object_or_404(Course, id=course_id)
    clean_expired_enrollments.apply_async(args=[course.id])
    return JsonResponse({'status': 'Задача запущена', 'course': course.title})
