from django.urls import include, path
from rest_framework.routers import DefaultRouter

from education_app.views.course import CourseViewSet, ModuleViewSet
from education_app import views

router = DefaultRouter()
router.register('modules', ModuleViewSet, basename='modules')
router.register('courses', CourseViewSet, basename='courses')

urlpatterns = [
    path('', include(router.urls)),
    path('run_cleanup/<int:course_id>/', views.course.run_cleanup_view, name='run_cleanup'),
]
