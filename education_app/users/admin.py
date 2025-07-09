from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff')
    fieldsets = (
        ('Учётные данные', {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(User, CustomUserAdmin)
