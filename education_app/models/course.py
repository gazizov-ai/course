from typing import Any

from django.db import models
from django.utils import timezone

from education_app.models.chat import Chat
from education_app.consts import TaskType
from base.models import BaseModel


class Tag(models.Model):
    title = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Course(BaseModel):
    title = models.CharField(max_length=50, verbose_name='Название курса')
    description = models.TextField(verbose_name='Описание курса', null=True)
    tags = models.ManyToManyField(Tag, related_name='courses', blank=True)
    avatar = models.ImageField(upload_to='course_avatars/', blank=True, null=True)
    duration_days = models.PositiveIntegerField(verbose_name='Длительность курса (в днях)', default=30)
    end_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Дата и время окончания курса')
    chat = models.OneToOneField(Chat, on_delete=models.SET_NULL, null=True, blank=True, related_name='course')

    def __str__(self) -> str:
        return self.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.end_datetime:
            self.end_datetime = timezone.now() + timezone.timedelta(days=self.duration_days)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    avatar = models.ImageField(upload_to='module_avatars/', blank=True, null=True)
    title = models.CharField(max_length=50, verbose_name='Название модуля')
    content = models.TextField(verbose_name='Содержимое модуля')
    order = models.PositiveIntegerField(default=0, null=True)

    def __str__(self) -> str:
        return f'{self.course.title} - {self.title}'

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'
        ordering = ['order']


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    avatar = models.ImageField(upload_to='lesson_avatars/', blank=True, null=True)
    title = models.CharField(max_length=50, verbose_name='Название урока')
    content = models.TextField(verbose_name='Содержимое урока')
    questions = models.ManyToManyField('education_app.Question', related_name='questions', blank=True)
    type = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.LECTURE, verbose_name='Тип урока')

    def __str__(self):
        return f'{self.type}: {self.title}'

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'


class Question(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название вопроса')
    content = models.TextField(verbose_name='Текст вопроса')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField(verbose_name='Текст ответа')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'