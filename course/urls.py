from django.urls import include, path
from rest_framework.routers import DefaultRouter

from course.views import CourseViewSet, ModuleViewSet

from . import views

router = DefaultRouter()
router.register('modules', ModuleViewSet, basename='modules')
router.register('courses', CourseViewSet, basename='courses')

urlpatterns = [
    path('', include(router.urls)),
    path('run_cleanup/<int:course_id>/', views.run_cleanup_view, name='run_cleanup'),
]
