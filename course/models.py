from typing import Any

from django.db import models
from django.utils import timezone

from chat.models import Chat


class Course(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название курса')
    description = models.TextField(verbose_name='Описание курса', null=True)
    avatar = models.ImageField(upload_to='course_avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration_days = models.PositiveIntegerField(verbose_name='Длительность курса (в днях)', default=30)
    end_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Дата и время окончания курса')
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE, null=True, blank=True, related_name='course')

    def __str__(self) -> str:
        return self.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.end_datetime:
            self.end_datetime = timezone.now() + timezone.timedelta(days=self.duration_days)
        super().save(*args, **kwargs)


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    avatar = models.ImageField(upload_to='module_avatars/', blank=True, null=True)
    title = models.CharField(max_length=50, verbose_name='Название модуля')
    content = models.TextField(verbose_name='Содержимое модуля')
    order = models.PositiveIntegerField(default=0, null=True)

    def __str__(self) -> str:
        return f'{self.course.title} - {self.title}'
