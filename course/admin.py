from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet
from django.http import HttpRequest

from course.tasks import clean_expired_enrollments

from .models import Course, Module


@admin.action(description='Запустить очистку для курса')
def run_cleanup(modeladmin: ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    for course in queryset:
        clean_expired_enrollments.apply_async(args=[course.id])


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'end_datetime', 'created_at']
    actions = [run_cleanup]


admin.site.register(Module)
