import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from education_app.consts import Role
from education_app.models.course import Course
from rest_framework.test import APIClient


@pytest.fixture
def User():
    return get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Неаутентифицированный API клиент."""
    return APIClient()


@pytest.fixture
def user_factory(User):
    def make_user(**kwargs):
        defaults = dict(
            username='gleb',
            password='pass',
            email='user@example.com',
            first_name='Name',
            last_name='Surname',
        )
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return make_user


@pytest.mark.django_db
def test_user_str_and_default_role(User) -> None:
    """Создаем пользователя, проверяем дефолтную роль."""
    user = User.objects.create_user(username="test", password="secret")
    assert str(user) == "test"
    assert user.role == Role.STUDENT
    assert user.phone is None


@pytest.mark.django_db
def test_user_courses_relationship(User) -> None:
    """Проверяем many-to-many между курсом и юзером."""
    user = User.objects.create_user(username="user1", password="secret")
    course = Course.objects.create(title="course 1")
    user.courses.add(course)
    assert course in user.courses.all()
    assert user in course.users.all()


@pytest.mark.django_db
def test_api_create_user(api_client: APIClient, User) -> None:
    """Проверка ручки create."""
    data = {
        "username": "gleb",
        "password": "pass1234",
        "email": "api@example.com",
        "first_name": "Api",
        "last_name": "User",
    }
    response = api_client.post("/api/users/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username="gleb").exists()


@pytest.mark.django_db
def test_api_list_requires_auth(api_client: APIClient) -> None:
    """Попробовать retrieve без логина."""
    response = api_client.get("/api/users/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_api_list_authenticated(api_client: APIClient, user_factory) -> None:
    """Проверка list."""
    u1 = user_factory(username="u1")
    user_factory(username="u2")
    api_client.force_authenticate(user=u1)
    response = api_client.get("/api/users/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_api_retrieve_requires_auth(api_client: APIClient, user_factory) -> None:
    """Попробовать retrieve без логина."""
    target = user_factory(username="target")
    response = api_client.get(f"/api/users/{target.id}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_api_retrieve_authenticated(api_client: APIClient, user_factory) -> None:
    """Проверка retrieve."""
    auth_user = user_factory(username="auth")
    target = user_factory(username="target")
    api_client.force_authenticate(user=auth_user)
    response = api_client.get(f"/api/users/{target.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == target.id


@pytest.mark.django_db
def test_api_update_self(api_client: APIClient, user_factory, User) -> None:
    """Проверка апдейта самого себя (должно пройти)."""
    user = user_factory(username="bob", email="b@example.com", first_name="Bob", last_name="Old")
    api_client.force_authenticate(user=user)
    payload = {
        "username": "usr",
        "email": "test@example.com",
        "first_name": "almas",
        "last_name": "surname",
        "password": "strong!",
    }
    response = api_client.put(f"/api/users/{user.id}/", payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.first_name == "almas"
    assert user.last_name == "surname"


@pytest.mark.django_db
def test_api_update_other_forbidden(api_client: APIClient, user_factory) -> None:
    """Нельзя апдейтить другого юзера под студентом."""
    user1 = user_factory(username="u1")
    user2 = user_factory(username="u2")
    api_client.force_authenticate(user=user1)
    payload = {
        "username": "u2",
        "email": "u2@example.com",
        "first_name": "Changed",
        "last_name": "User",
        "password": "pass",
    }
    response = api_client.put(f"/api/users/{user2.id}/", payload, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_api_update_other_as_staff(api_client: APIClient, user_factory) -> None:
    """Можно апдейтить других под стаффом."""
    staff = user_factory(username="staff", is_staff=True)
    target = user_factory(username="target", email="t@example.com")
    api_client.force_authenticate(user=staff)
    payload = {
        "username": "target",
        "email": "t@example.com",
        "first_name": "New",
        "last_name": "Name",
        "password": "pass",
    }
    response = api_client.put(f"/api/users/{target.id}/", payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    target.refresh_from_db()
    assert target.first_name == "New"


@pytest.mark.django_db
def test_api_partial_update_self(api_client: APIClient, user_factory) -> None:
    """Можно патчить самого себя."""
    user = user_factory(username="part")
    api_client.force_authenticate(user=user)
    response = api_client.patch(
        f"/api/users/{user.id}/",
        {"first_name": "Patch"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.first_name == "Patch"


@pytest.mark.django_db
def test_api_destroy_user(api_client: APIClient, user_factory, User) -> None:
    """Проверка delete."""
    user1 = user_factory(username="u1")
    user2 = user_factory(username="u2")
    api_client.force_authenticate(user=user1)
    response = api_client.delete(f"/api/users/{user2.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not User.objects.filter(id=user2.id).exists()