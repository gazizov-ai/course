from django.urls import include, path
from rest_framework.routers import DefaultRouter

from education_app.views.course import CourseViewSet, ModuleViewSet, LessonViewSet, QuestionViewSet, AnswerViewSet, TagViewSet
from education_app import views

router = DefaultRouter()
router.register('courses', CourseViewSet, basename='courses')
router.register('modules', ModuleViewSet, basename='modules')
router.register('lessons', LessonViewSet, basename='lessons')
router.register('questions', QuestionViewSet, basename='questions')
router.register('answers', AnswerViewSet, basename='answers')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('run_cleanup/<int:course_id>/', views.course.run_cleanup_view, name='run_cleanup'),
]
