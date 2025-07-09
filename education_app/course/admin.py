from django.contrib import admin

from .models import Course, Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'end_datetime', 'created_at']


admin.site.register(Module)
