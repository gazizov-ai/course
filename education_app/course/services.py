import typing
from django.utils import timezone
from education_app.chat.models import Chat, ChatParticipant
from .models import Course


def save_course(course: Course) -> None:
    if not course.end_datetime:
        course.end_datetime = timezone.now() + timezone.timedelta(days=course.duration_days)
    course.save()


def create_course_with_users_and_chat(validated_data: dict[str, typing.Any]) -> Course:
    users = validated_data.pop('users', [])
    course = Course.objects.create(**validated_data)

    chat = Chat.objects.create(name=course.title, is_group=True)
    course.chat = chat
    course.save()

    if users:
        course.users.set(users)
        ChatParticipant.objects.bulk_create([
            ChatParticipant(chat=chat, user=user) for user in users
        ])

    return course


def update_course_users_in_service(course: Course, user_ids: list[int]) -> None:
    course.users.exclude(id__in=user_ids).clear()

    chat = course.chat
    if chat:
        ChatParticipant.objects.filter(chat=chat).exclude(user__id__in=user_ids).delete()

        new_participants = [ChatParticipant(chat=chat, user_id=user_id) for user_id in user_ids]
        ChatParticipant.objects.bulk_create(new_participants)

    course.save()
