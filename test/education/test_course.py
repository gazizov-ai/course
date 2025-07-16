import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from education_app.models.course import Course

User = get_user_model()


@pytest.mark.django_db
def test_create_course() -> None:
    user = User.objects.create_user(username='testuser', password='testpass')
    client = APIClient()
    client.force_authenticate(user)

    url = reverse('courses-list')
    payload = {
        'title': 'Тестовый курс',
        'description': 'Описание курса',
        'duration_days': 10,
    }
    response = client.post(url, payload, format='json')

    assert response.status_code == 201
    assert response.data['title'] == payload['title']
    assert Course.objects.count() == 1


@pytest.mark.django_db
def test_update_course_users() -> None:
    user = User.objects.create_user(username='admin', password='adminpass', is_staff=True)
    student1 = User.objects.create_user(username='student1', password='123')
    student2 = User.objects.create_user(username='student2', password='123')

    client = APIClient()
    client.force_authenticate(user)

    course = Course.objects.create(title='Test Course', duration_days=7)

    url = reverse('courses-update-course-users', args=[course.id])
    payload = {'user_ids': [student1.id, student2.id]}

    response = client.post(url, payload, format='json')

    assert response.status_code == 200
    course.refresh_from_db()
    assert course.users.count() == 2
    assert course.users.filter(id=student1.id).exists()
    assert course.users.filter(id=student2.id).exists()


@pytest.mark.django_db
def test_get_course_detail() -> None:
    user = User.objects.create_user(username='testuser', password='testpass')
    client = APIClient()
    client.force_authenticate(user)

    course = Course.objects.create(title='Detail Course', duration_days=14)
    url = reverse('courses-detail', args=[course.id])

    response = client.get(url)

    assert response.status_code == 200
    assert response.data['title'] == course.title