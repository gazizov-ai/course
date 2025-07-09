from django.conf import settings
from django.db import models


class Chat(models.Model):
    name = models.CharField(max_length=255, blank=True)
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name or f'{"Group" if self.is_group else "Private"} Chat #{self.id}'


class ChatParticipant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_participations'
    )
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.user} in {self.chat}'

    class Meta:
        unique_together = ('user', 'chat')


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.sender.username}: {self.text[:30]}'


class MessageAttachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)

    def __str__(self):
        return f'Attachment for message {self.message.id}'