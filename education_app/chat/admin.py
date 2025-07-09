from django.contrib import admin

from .models import Chat, ChatParticipant, Message


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

