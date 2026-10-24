import os

# Config is imported when the application package is imported. Keep tests independent
# of a developer's local environment and never use a production secret here.
os.environ.setdefault("SECRET_KEY", "test-only-secret-key")

import pytest

from app import create_app, db


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-only-secret-key"
    JWT_SECRET_KEY = "test-only-jwt-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False


@pytest.fixture

def app():
    application = create_app(TestConfig)

    with application.app_context():
        db.create_all()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture

def client(app):
    return app.test_client()
