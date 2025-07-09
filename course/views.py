from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, JsonResponse
from django.http import JsonResponse as JsonResponseType
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from chat.models import ChatParticipant
from course.tasks import clean_expired_enrollments
from users.models import User

from .models import Course, Module
from .serializers import CourseSerializer, ModuleSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminUser]

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
        new_user_ids = request.data.get('user_ids', [])

        if not isinstance(new_user_ids, list):
            return Response({'detail': 'user_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)

        current_user_ids = set(course.users.values_list('id', flat=True))
        new_user_ids_set = set(new_user_ids)

        to_add = new_user_ids_set - current_user_ids
        to_remove = current_user_ids - new_user_ids_set

        if to_remove:
            users_to_remove = User.objects.filter(id__in=to_remove)
            for user in users_to_remove:
                course.users.remove(user)
                if course.chat:
                    ChatParticipant.objects.filter(chat=course.chat, user=user).delete()

        if to_add:
            users_to_add = User.objects.filter(id__in=to_add)
            for user in users_to_add:
                course.users.add(user)
                if course.chat:
                    ChatParticipant.objects.get_or_create(chat=course.chat, user=user)

        return Response({'detail': 'Course users updated successfully'}, status=status.HTTP_200_OK)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer



@user_passes_test(lambda u: u.is_staff)
def run_cleanup_view(request: HttpRequest, course_id: int) -> JsonResponseType:
    course = get_object_or_404(Course, id=course_id)
    clean_expired_enrollments.apply_async(args=[course.id])
    return JsonResponse({'status': 'Задача запущена', 'course': course.title})
