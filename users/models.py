from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    courses = models.ManyToManyField('course.Course', related_name='users', blank=True)

    class Role(models.TextChoices):
        STUDENT = 'student', 'Ученик'
        MENTOR = 'mentor', 'Ментор'
        CURATOR = 'curator', 'Куратор'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT, verbose_name='Роль')

    def __str__(self) -> str:
        return self.username
