from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions, viewsets

from education_app.models.users import User
from education_app.serializers.users import UserSerializer



@extend_schema(
    request=UserSerializer,
    responses={201: UserSerializer},
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
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        elif self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy", "list"]:
            return [permissions.IsAdminUser()]
        return super().get_permissions()
