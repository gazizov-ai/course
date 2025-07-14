from django.db import models


class Role(models.TextChoices):
    STUDENT = 'student', 'Ученик'
    MENTOR = 'mentor', 'Ментор'
    CURATOR = 'curator', 'Куратор'


class TaskType(models.TextChoices):
    LECTURE = 'lecture', 'Лекция'
    PRACTICE = 'practice', 'Практика'
    TEST = 'test', 'Тестирование'