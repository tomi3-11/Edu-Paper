from flask_jwt_extended import create_access_token

from app import db
from app.models import User


ADMIN_USERS_URL = "/api/v1/admin/users"


def make_user(app, username, email, role="member"):
    with app.app_context():
        user = User(username=username, email=email, role=role)
        user.set_password("StrongPass123")
        db.session.add(user)
        db.session.commit()
        return user.id


def auth_header(user_id):
    token = create_access_token(identity=str(user_id))
    return {"Authorization": f"Bearer {token}"}


def test_admin_users_endpoint_requires_authentication(client):
    response = client.get(ADMIN_USERS_URL)

    assert response.status_code == 401


def test_admin_users_endpoint_forbids_member(app, client):
    user_id = make_user(
        app,
        username="regularstudent",
        email="regular@example.com",
    )

    response = client.get(
        ADMIN_USERS_URL,
        headers=auth_header(user_id),
    )

    assert response.status_code == 403


def test_admin_users_endpoint_returns_safe_user_fields(app, client):
    make_user(
        app,
        username="firststudent",
        email="first@example.com",
    )
    make_user(
        app,
        username="secondstudent",
        email="second@example.com",
        role="admin",
    )
    admin_id = make_user(
        app,
        username="requestingadmin",
        email="admin@example.com",
        role="admin",
    )

    response = client.get(
        ADMIN_USERS_URL,
        headers=auth_header(admin_id),
    )

    assert response.status_code == 200
    users = response.get_json()["users"]
    assert len(users) == 3
    assert users[0] == {
        "id": 1,
        "username": "firststudent",
        "email": "first@example.com",
        "role": "member",
    }
    assert all("password_hash" not in user for user in users)
    assert all("reset_token" not in user for user in users)


def test_admin_users_endpoint_returns_empty_list_when_no_users(app, client):
    admin_id = make_user(
        app,
        username="soleadmin",
        email="soleadmin@example.com",
        role="admin",
    )

    response = client.get(
        ADMIN_USERS_URL,
        headers=auth_header(admin_id),
    )

    assert response.status_code == 200
    assert response.get_json()["users"] == [
        {
            "id": admin_id,
            "username": "soleadmin",
            "email": "soleadmin@example.com",
            "role": "admin",
        }
    ]
