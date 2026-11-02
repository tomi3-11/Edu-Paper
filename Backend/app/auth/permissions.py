from functools import wraps

from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models import User


def role_required(*allowed_roles):
    """Require a valid JWT and one of the user's current database roles."""
    if not allowed_roles:
        raise ValueError("At least one allowed role must be provided.")

    def decorator(view_function):
        @wraps(view_function)
        @jwt_required()
        def wrapped(*args, **kwargs):
            identity = get_jwt_identity()

            try:
                user_id = int(identity)
            except (TypeError, ValueError):
                return {"message": "Invalid user identity."}, 401

            user = db.session.get(User, user_id)
            if user is None:
                return {"message": "User not found."}, 404

            if user.role not in allowed_roles:
                return {"message": "Forbidden: insufficient permissions."}, 403

            return view_function(*args, **kwargs)

        return wrapped

    return decorator
