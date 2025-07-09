from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions, viewsets

from . import models, serializers


@extend_schema(
    request=serializers.UserSerializer,
    responses={201: serializers.UserSerializer},
    examples=[
        OpenApiExample(
            'User creation example',
            value={
                'username': 'username',
                'password': '<PASSWORD>',
                'email': 'pochta@mail.ru',
                'first_name': 'Name',
                'last_name': 'Lastname',
                'phone': '79177777777',
                'course_ids': [1, 2],
            },
            request_only=True,
        )
    ],
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
