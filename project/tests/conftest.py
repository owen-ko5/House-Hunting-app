import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("FLASK_ENV", "development")

import pytest

from app import create_app
from app import db as _db


@pytest.fixture()
def app():
    application = create_app()
    application.config.update(TESTING=True)
    application.config["RATELIMIT_ENABLED"] = False  # tests shouldn't trip rate limits

    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
