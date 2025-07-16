import pytest
from django.contrib.auth import get_user_model
from education_app.consts import Role
from education_app.models.course import Course
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_user_str_and_default_role():
    User = get_user_model()
    user = User.objects.create_user(username="john", password="secret")
    assert str(user) == "john"
    assert user.role == Role.STUDENT
    assert user.phone is None


@pytest.mark.django_db
def test_user_courses_relationship():
    User = get_user_model()
    user = User.objects.create_user(username="alice", password="secret")
    course = Course.objects.create(title="Course 1")
    user.courses.add(course)
    assert course in user.courses.all()
    assert user in course.users.all()


@pytest.mark.django_db
def test_api_create_user():
    client = APIClient()
    data = {
        "username": "apiuser",
        "password": "pass1234",
        "email": "api@example.com",
        "first_name": "Api",
        "last_name": "User",
    }
    response = client.post("/api/users/", data, format="json")
    assert response.status_code == 201
    User = get_user_model()
    assert User.objects.filter(username="apiuser").exists()


@pytest.mark.django_db
def test_api_list_requires_auth():
    response = APIClient().get("/api/users/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_api_list_authenticated():
    User = get_user_model()
    u1 = User.objects.create_user(
        username="u1", password="pass", email="u1@example.com", first_name="A", last_name="A"
    )
    User.objects.create_user(
        username="u2", password="pass", email="u2@example.com", first_name="B", last_name="B"
    )
    client = APIClient()
    client.force_authenticate(user=u1)
    response = client.get("/api/users/")
    assert response.status_code == 200
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_api_retrieve_requires_auth():
    User = get_user_model()
    target = User.objects.create_user(
        username="target", password="pass", email="t@example.com", first_name="A", last_name="B"
    )
    response = APIClient().get(f"/api/users/{target.id}/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_api_retrieve_authenticated():
    User = get_user_model()
    auth_user = User.objects.create_user(
        username="auth", password="pass", email="auth@example.com", first_name="A", last_name="B"
    )
    target = User.objects.create_user(
        username="target", password="pass", email="t@example.com", first_name="A", last_name="B"
    )
    client = APIClient()
    client.force_authenticate(user=auth_user)
    response = client.get(f"/api/users/{target.id}/")
    assert response.status_code == 200
    assert response.data["id"] == target.id


@pytest.mark.django_db
def test_api_update_self():
    User = get_user_model()
    user = User.objects.create_user(
        username="bob", password="pass", email="b@example.com", first_name="Bob", last_name="Old"
    )
    client = APIClient()
    client.force_authenticate(user=user)
    payload = {
        "username": "bob",
        "email": "b@example.com",
        "first_name": "Bobby",
        "last_name": "New",
        "password": "pass",
    }
    response = client.put(f"/api/users/{user.id}/", payload, format="json")
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == "Bobby"


@pytest.mark.django_db
def test_api_update_other_forbidden():
    User = get_user_model()
    user1 = User.objects.create_user(
        username="u1", password="pass", email="u1@example.com", first_name="A", last_name="A"
    )
    user2 = User.objects.create_user(
        username="u2", password="pass", email="u2@example.com", first_name="B", last_name="B"
    )
    client = APIClient()
    client.force_authenticate(user=user1)
    payload = {
        "username": "u2",
        "email": "u2@example.com",
        "first_name": "Changed",
        "last_name": "User",
        "password": "pass",
    }
    response = client.put(f"/api/users/{user2.id}/", payload, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_api_update_other_as_staff():
    User = get_user_model()
    staff = User.objects.create_user(
        username="staff", password="pass", email="s@example.com", first_name="S", last_name="S", is_staff=True
    )
    target = User.objects.create_user(
        username="target", password="pass", email="t@example.com", first_name="T", last_name="T"
    )
    client = APIClient()
    client.force_authenticate(user=staff)
    payload = {
        "username": "target",
        "email": "t@example.com",
        "first_name": "New",
        "last_name": "Name",
        "password": "pass",
    }
    response = client.put(f"/api/users/{target.id}/", payload, format="json")
    assert response.status_code == 200
    target.refresh_from_db()
    assert target.first_name == "New"


@pytest.mark.django_db
def test_api_partial_update_self():
    User = get_user_model()
    user = User.objects.create_user(
        username="part", password="pass", email="p@example.com", first_name="P", last_name="P"
    )
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.patch(
        f"/api/users/{user.id}/",
        {"first_name": "Patch"},
        format="json",
    )
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == "Patch"


@pytest.mark.django_db
def test_api_destroy_user():
    User = get_user_model()
    user1 = User.objects.create_user(
        username="u1", password="pass", email="u1@example.com", first_name="A", last_name="A"
    )
    user2 = User.objects.create_user(
        username="u2", password="pass", email="u2@example.com", first_name="B", last_name="B"
    )
    client = APIClient()
    client.force_authenticate(user=user1)
    response = client.delete(f"/api/users/{user2.id}/")
    assert response.status_code == 204
    assert not User.objects.filter(id=user2.id).exists()
