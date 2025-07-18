from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from education_app.models.chat import Chat, ChatParticipant, Message
from education_app.models.course import Course, Module, Lesson, Question, Answer, Tag
from education_app.models.users import User


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_group', 'created_at')
    search_fields = ('name',)


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'chat', 'joined_at')
    list_filter = ('chat', 'user')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'text', 'created_at')
    list_filter = ('chat', 'sender')
    search_fields = ('text',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'end_datetime', 'created_at']


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff')
    fieldsets = (
        ('Учётные данные', {'fields': ('username', 'password')}),
        (
            'Личная информация',
            {'fields': ('first_name', 'last_name', 'email', 'phone')},
        ),
        (
            'Права доступа',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Tag)
admin.site.register(User, CustomUserAdmin)
