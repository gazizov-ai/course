from education_app.chat.models import ChatParticipant
from education_app.course.models import Course
from .models import User


def set_courses_and_chats(user: User, courses: list[Course]) -> None:
    user.courses.set(courses)
    for course in courses:
        if course.chat:
            ChatParticipant.objects.get_or_create(chat=course.chat, user=user)


def create_user(validated_data: dict) -> User:
    courses = validated_data.pop('courses', [])
    password = validated_data.pop('password')

    user = User.objects.create(**validated_data)
    user.set_password(password)
    user.save()

    if courses:
        set_courses_and_chats(user, courses)

    return user


def update_user(instance: User, validated_data: dict) -> User:
    courses = validated_data.pop('courses', None)
    password = validated_data.pop('password', None)

    for attr, value in validated_data.items():
        setattr(instance, attr, value)

    if password:
        instance.set_password(password)

    instance.save()

    if courses is not None:
        set_courses_and_chats(instance, courses)

    return instance