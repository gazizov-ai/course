from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView


from education_app.models.users import User
from education_app.serializers.users import UserSerializer, CustomTokenObtainPairSerializer


@extend_schema(
    request=UserSerializer,
    responses={201: UserSerializer},
    examples=[
        OpenApiExample(
            "User creation example",
            value={
                "username": "username",
                "password": "<PASSWORD>",
                "email": "pochta@mail.ru",
                "first_name": "Name",
                "last_name": "Lastname",
                "phone": "79177777777",
                "course_ids": [1, 2],
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
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if not request.user.is_staff:
            if instance != request.user:
                raise PermissionDenied("Вы можете обновлять только свой профиль.")

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if not request.user.is_staff:
            if instance != request.user:
                raise PermissionDenied("Вы можете обновлять только свой профиль.")

        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request: Request) -> Response:
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
