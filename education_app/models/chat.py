from django.conf import settings
from django.db import models

from base.models import BaseModel


class Chat(BaseModel):
    name = models.CharField(max_length=255, blank=True, verbose_name='Название')
    is_group = models.BooleanField('Групповой чат', default=False)

    def __str__(self) -> str:
        return self.name or f'{"Группа" if self.is_group else "Приватная"} Чат #{self.id}'

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'


class ChatParticipant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_participations',
        verbose_name='Пользователь',
    )
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='participants', verbose_name='Чат')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')

    class Meta:
        unique_together = ('user', 'chat')
        verbose_name = 'Участник чата'
        verbose_name_plural = 'Участники чата'

    def __str__(self) -> str:
        return f'{self.user} in {self.chat}'


class Message(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', verbose_name='Чат')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='messages',
        verbose_name='Отправитель',
    )
    text = models.TextField(blank=True, verbose_name='Текст')

    def __str__(self) -> str:
        return f'{self.sender.username}: {self.text[:300]}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-id']


class MessageAttachment(models.Model):
    message = models.ForeignKey(
        Message,
        verbose_name='Сообщения',
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    file = models.FileField('Файл (включая изображения)', upload_to='chat_files/', blank=True, null=True)

    class Meta:
        verbose_name = 'Вложение к сообщению'
        verbose_name_plural = 'Вложения к сообщениям'

    def __str__(self) -> str:
        return f'Вложение: {self.message.id}'
