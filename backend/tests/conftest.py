import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models import Category, User
from app.services.transaction_service import CATEGORY_SEEDS


@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "JWT_SECRET_KEY": "test-only-secret-that-is-long-enough",
        "CORS_ORIGINS": [],
    })
    with app.app_context():
        db.create_all()
        db.session.add_all([
            Category(key=key, label=label, transaction_type=kind)
            for key, label, kind in CATEGORY_SEEDS
        ])
        user = User(email="tester@example.com", password_hash="unused")
        db.session.add(user)
        db.session.commit()
        app.config["TEST_USER_ID"] = user.id
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity=str(app.config["TEST_USER_ID"]))
    return {"Authorization": f"Bearer {token}"}
