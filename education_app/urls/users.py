from django.urls import include, path
from rest_framework.routers import DefaultRouter

from education_app.views.users import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('api/', include(router.urls)),
]
