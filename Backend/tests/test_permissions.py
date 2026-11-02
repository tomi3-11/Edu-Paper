from flask_jwt_extended import create_access_token

from app import db
from app.auth.permissions import role_required
from app.models import User


PROTECTED_URL = "/api/v1/test/admin-only"


def make_user(app, role="member", username="permissionuser"):
    with app.app_context():
        user = User(
            username=username,
            email=f"{username}@example.com",
            role=role,
        )
        user.set_password("StrongPass123")
        db.session.add(user)
        db.session.commit()
        return user.id


def token_for(user_id):
    return create_access_token(identity=str(user_id))


def register_test_endpoint(app):
    @role_required("admin")
    def admin_only():
        return {"message": "Access granted."}, 200

    app.add_url_rule(
        PROTECTED_URL,
        view_func=admin_only,
        methods=["GET"],
    )


def test_role_protected_endpoint_rejects_missing_token(app, client):
    register_test_endpoint(app)

    response = client.get(PROTECTED_URL)

    assert response.status_code == 401


def test_role_protected_endpoint_forbids_member(app, client):
    register_test_endpoint(app)
    user_id = make_user(app, role="member")

    with app.app_context():
        token = token_for(user_id)

    response = client.get(
        PROTECTED_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.get_json()["message"] == "Forbidden: insufficient permissions."


def test_role_protected_endpoint_allows_admin(app, client):
    register_test_endpoint(app)
    user_id = make_user(app, role="admin", username="adminuser")

    with app.app_context():
        token = token_for(user_id)

    response = client.get(
        PROTECTED_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Access granted."


def test_role_protected_endpoint_returns_not_found_for_deleted_user(app, client):
    register_test_endpoint(app)
    user_id = make_user(app, role="admin", username="deletedadmin")

    with app.app_context():
        token = token_for(user_id)
        user = db.session.get(User, user_id)
        db.session.delete(user)
        db.session.commit()

    response = client.get(
        PROTECTED_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "User not found."
