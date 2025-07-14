from django.contrib.auth.models import AbstractUser
from django.db import models
from education_app.consts import Role

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    courses = models.ManyToManyField('education_app.Course', related_name='users', blank=True)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT, verbose_name='Роль')

    def __str__(self) -> str:
        return self.username