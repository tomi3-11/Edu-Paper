import pytest

from app import db
from app.models import User


REGISTER_URL = "/Api/register"
LOGIN_URL = "/Api/login"


def make_user(app, username="teststudent", email="student@example.com", password="StrongPass123"):
    with app.app_context():
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.mark.parametrize("url", [REGISTER_URL, LOGIN_URL])
@pytest.mark.parametrize(
    "body, content_type",
    [
        (None, None),
        ('{"email":', "application/json"),
        ("[]", "application/json"),
        ("null", "application/json"),
    ],
)
def test_auth_endpoints_reject_missing_malformed_or_non_object_json(
    client, url, body, content_type
):
    request_args = {}
    if body is not None:
        request_args["data"] = body
        request_args["content_type"] = content_type

    response = client.post(url, **request_args)

    assert response.status_code == 400
    assert response.get_json() == {
        "message": "Request body must be a JSON object."
    }


def test_registration_creates_user_with_hashed_password(app, client):
    response = client.post(
        REGISTER_URL,
        json={
            "username": "newstudent",
            "email": "newstudent@example.com",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered successfully"

    with app.app_context():
        user = User.query.filter_by(email="newstudent@example.com").one()
        assert user.username == "newstudent"
        assert user.password_hash != "StrongPass123"
        assert user.check_password("StrongPass123")


@pytest.mark.parametrize(
    "payload",
    [
        {
            "email": "not-an-email",
            "username": "student",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        },
        {
            "email": "student@example.com",
            "username": "student",
            "password": "short",
            "confirm_password": "short",
        },
        {
            "email": "student@example.com",
            "username": "student",
            "password": "StrongPass123",
            "confirm_password": "DifferentPass123",
        },
        {"email": "student@example.com"},
    ],
)
def test_registration_rejects_invalid_form_data(client, payload):
    response = client.post(REGISTER_URL, json=payload)

    assert response.status_code == 400
    assert isinstance(response.get_json(), dict)


def test_registration_rejects_duplicate_username(app, client):
    make_user(app, username="takenname", email="first@example.com")

    response = client.post(
        REGISTER_URL,
        json={
            "username": "takenname",
            "email": "second@example.com",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        },
    )

    assert response.status_code == 409
    assert response.get_json()["message"] == "Username already exists"


def test_registration_rejects_duplicate_email(app, client):
    make_user(app, username="firststudent", email="taken@example.com")

    response = client.post(
        REGISTER_URL,
        json={
            "username": "secondstudent",
            "email": "taken@example.com",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        },
    )

    assert response.status_code == 409
    assert response.get_json()["message"] == "Email already exists"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"email": "student@example.com"},
        {"password": "StrongPass123"},
        {"email": "", "password": "StrongPass123"},
        {"email": "student@example.com", "password": ""},
    ],
)
def test_login_rejects_missing_credentials(client, payload):
    response = client.post(LOGIN_URL, json=payload)

    assert response.status_code == 400
    assert response.get_json()["message"] == "email or password required"


def test_login_rejects_unknown_email(client):
    response = client.post(
        LOGIN_URL,
        json={"email": "unknown@example.com", "password": "StrongPass123"},
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == "Invalid email or password."


def test_login_rejects_wrong_password(app, client):
    make_user(app)

    response = client.post(
        LOGIN_URL,
        json={"email": "student@example.com", "password": "WrongPass123"},
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == "Invalid email or password."


def test_login_returns_access_token_for_valid_credentials(app, client):
    user_id = make_user(app, username="validstudent", email="valid@example.com")

    response = client.post(
        LOGIN_URL,
        json={"email": "valid@example.com", "password": "StrongPass123"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body.get("access_token"), str)
    assert body["access_token"]
    assert body["message"] == "Login In successfully"
