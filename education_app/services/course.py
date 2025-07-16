import typing

from django.contrib.auth import get_user_model
from django.utils import timezone

from education_app.models.chat import Chat, ChatParticipant
from education_app.models.course import Course

User = get_user_model()


class CourseService:
    @staticmethod
    def save_course(course: Course) -> None:
        if not course.end_datetime:
            course.end_datetime = timezone.now() + timezone.timedelta(days=course.duration_days)
        course.save()

    @staticmethod
    def create_course_with_users_and_chat(
        validated_data: dict[str, typing.Any],
    ) -> Course:
        users = validated_data.pop('users', [])
        course = Course.objects.create(**validated_data)

        chat = Chat.objects.create(name=course.title, is_group=True)
        course.chat = chat
        course.save()

        if users:
            course.users.set(users)
            ChatParticipant.objects.bulk_create([ChatParticipant(chat=chat, user=user) for user in users])

        return course

    @staticmethod
    def update_course_users(course: Course, user_ids: list[int]) -> None:
        users = User.objects.filter(id__in=user_ids)
        course.users.set(users)

        chat = course.chat
        if chat:
            ChatParticipant.objects.filter(chat=chat).exclude(user__in=users).delete()

            existing_ids = set(ChatParticipant.objects.filter(chat=chat).values_list('user_id', flat=True))
            new_ids = set(users.values_list('id', flat=True)) - existing_ids

            ChatParticipant.objects.bulk_create([ChatParticipant(chat=chat, user_id=user_id) for user_id in new_ids])

        course.save()


class UserService:
    @staticmethod
    def update_user_courses(user: User, course_ids: list[int]) -> None:
        courses = Course.objects.filter(id__in=course_ids)
        user.courses.set(courses)
        user.save()
