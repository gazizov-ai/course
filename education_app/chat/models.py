from django.conf import settings
from django.db import models


class Chat(models.Model):
    name = models.CharField(max_length=255, blank=True, verbose_name='Название')
    is_group = models.BooleanField(default=False,verbose_name='Групповой чат')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name= 'Дата создания')

    def __str__(self) -> str:
        return self.name or f'{"Group" if self.is_group else "Private"} Chat #{self.id}'

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

class ChatParticipant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_participations',
        verbose_name='Пользователь'
    )
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Чат'
    )
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')

    def __str__(self) -> str:
        return f'{self.user} in {self.chat}'

    class Meta:
        unique_together = ('user', 'chat')
        verbose_name = 'Участник чата'
        verbose_name_plural = 'Участники чата'


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages',verbose_name='Чат')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages',verbose_name='Отправитель')
    text = models.TextField(blank=True, verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')

    def __str__(self) -> str:
        return f'{self.sender.username}: {self.text[:30]}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

class MessageAttachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments', verbose_name='Сообщения')
    file = models.FileField(upload_to='chat_files/', blank=True, null=True,verbose_name='Файл')
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True, verbose_name='Изображение')

    def __str__(self):
        return f'Attachment for message {self.message.id}'

    class Meta:
        verbose_name = 'Вложение к сообщению'
        verbose_name_plural = 'Вложения к сообщениям'