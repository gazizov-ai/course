import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from chat.models import ChatParticipant, Message
from course.models import Course

logger = logging.getLogger(__name__)


@shared_task
def clean_expired_enrollments(course_id: int) -> None:
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        logger.error(f'Курс с ID {course_id} не найден.')
        return

    if course.end_datetime < timezone.now() - timedelta(days=30):
        chat = getattr(course, 'chat', None)
        if chat:
            ChatParticipant.objects.filter(chat=chat).delete()
            Message.objects.filter(chat=chat).delete()

        if hasattr(course, 'students'):
            course.students.clear()

        logger.info(f'Курс {course.title} очищен от участников и сообщений.')
    else:
        logger.info(f'Курс {course.title} ещё не завершён.')


def schedule_cleanup(course_id: int) -> None:
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        logger.error(f'Курс с ID {course_id} не найден для планирования задачи.')
        return

    time_to_cleanup = course.end_datetime - timezone.now()
    cleanup_time = max(time_to_cleanup.total_seconds(), 0)

    clean_expired_enrollments.apply_async(countdown=cleanup_time, args=[course_id])
