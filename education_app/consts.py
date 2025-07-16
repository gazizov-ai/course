from django.db import models


class Role(models.TextChoices):
    STUDENT = "student", "Ученик"
    MENTOR = "mentor", "Ментор"
    CURATOR = "curator", "Куратор"
