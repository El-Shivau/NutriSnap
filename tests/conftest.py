"""
pytest Configuration and Fixtures
===================================

This conftest.py defines shared fixtures available to all test files.

Key Fixtures
------------
- app       : A Flask app instance configured for testing (in-memory SQLite DB).
- client    : A Flask test client for making HTTP requests.
- db_setup  : Creates all database tables before each test, drops after.
- test_user : A pre-created user in the test database.

Usage
-----
Import fixtures by name in any test function:

    def test_something(client, test_user):
        response = client.get('/dashboard')
        assert response.status_code == 302  # redirected to login

pytest auto-discovers fixtures from conftest.py automatically — no
explicit imports needed.
"""

import pytest

from backend.app import create_app
from backend.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """
    Create a Flask application configured for the test environment.

    - Uses an in-memory SQLite database.
    - CSRF protection is disabled.
    - Bcrypt rounds reduced to 4 for speed.

    The app is created once per test session (scope='session').
    """
    flask_app = create_app("testing")

    # Establish application context
    ctx = flask_app.app_context()
    ctx.push()

    yield flask_app

    ctx.pop()


@pytest.fixture(scope="function")
def db(app):
    """
    Provide a clean database for each test function.

    Creates all tables before the test and drops them after.
    This ensures each test starts with a completely clean slate.
    """
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """
    Provide a Flask test client for making HTTP requests.

    Use this fixture in integration tests:

        def test_login_page(client):
            response = client.get('/auth/login')
            assert response.status_code == 200
    """
    return app.test_client()


@pytest.fixture(scope="function")
def test_user(db):
    """
    Create a sample user in the test database.

    Returns the User object with:
        - username  : 'testuser'
        - email     : 'test@example.com'
        - password  : 'TestPass1' (plaintext — hashed internally)
    """
    from backend.extensions import bcrypt
    from backend.models.user import User

    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=bcrypt.generate_password_hash("TestPass1").decode("utf-8"),
    )
    db.session.add(user)
    db.session.commit()
    return user
