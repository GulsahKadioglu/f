# -*- coding: utf-8 -*-
"""conftest.py

This file contains shared fixtures for the pytest test suite.
Fixtures defined here are automatically discovered by pytest and can be used in
any test function within the test suite. This file is used to set up the
test environment, including database connections, test clients, and mock objects.

Purpose:
- To provide a centralized location for test setup and configuration.
- To define reusable fixtures for database sessions, API test clients, and
  authenticated users.
- To ensure a clean and consistent state for each test function.

Key Components:
- `db_engine`, `db_session`: Fixtures to set up an in-memory SQLite database
  for testing, ensuring that each test function gets a fresh, isolated database session.
- `client`: A fixture that provides a FastAPI `TestClient` instance, configured
  to use the test database.
- `test_user`, `test_admin_user`: Fixtures that create a standard user and an
  admin user in the test database for use in authenticated endpoint tests.
- `test_token`, `test_admin_token`: Fixtures that generate JWT access tokens for
  the test users.
- Mocking fixtures: Mocks for external services like Redis (for rate limiting)
  to prevent actual network calls during tests.
"""

import os
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# --- Initial Setup -------------------------------------------------------------
load_dotenv(dotenv_path="backend/.env.test")
os.environ["TESTING"] = "1"
if "SECRET_KEY" not in os.environ:
    os.environ["SECRET_KEY"] = "testsecretkey"

# --- Imports from our application ----------------------------------------------

# By using absolute imports from the project root, we ensure that pytest 
# can correctly discover and run tests regardless of the execution path.
from backend.core.security import create_access_token
from backend.crud import user as user_crud
from backend.db.base import Base
from backend.db.session import get_db
from backend.main import app
from backend.models.user import User
from backend.schemas.user import UserCreate
from backend.worker import celery_app

# --- Global Test Setup ---------------------------------------------------------


@pytest.fixture(autouse=True)
def setup_celery_for_tests():
    """Fixture to configure Celery for testing.

    This fixture runs automatically for every test (`autouse=True`).
    It sets Celery to run tasks eagerly in the same process, so background
    tasks are executed synchronously during tests without needing a separate
    Celery worker.
    """
    celery_app.conf.update(task_always_eager=True)


@pytest.fixture(autouse=True)
def mock_fastapi_limiter():
    """Fixture to mock the FastAPI rate limiter.

    This fixture runs automatically for every test (`autouse=True`).
    It patches the `init` and `close` methods of the `FastAPILimiter` to prevent
    it from trying to connect to a Redis instance during tests.
    """
    # Mock FastAPILimiter.init and .close to prevent actual Redis connection attempts
    with (
        patch(
            "fastapi_limiter.FastAPILimiter.init", new_callable=AsyncMock
        ) as mock_init,
        patch(
            "fastapi_limiter.FastAPILimiter.close", new_callable=AsyncMock
        ) as mock_close,
    ):
        yield


# --- Database Fixtures ---------------------------------------------------------

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def db_engine():
    """Fixture to create a test database engine.

    This fixture has a "session" scope, meaning it is created only once per
    test session. It sets up an in-memory SQLite database and creates all
    tables defined in the application's models.
    """
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)  # Ensure all models are imported before this
    yield engine


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Fixture to create a new database session for each test function.

    This fixture has a "function" scope, meaning it runs for each test function.
    It creates a new database session within a transaction, yields the session
    to the test, and then rolls back the transaction after the test is complete.
    This ensures that each test runs in isolation and does not affect other tests.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# --- Test Client Fixture -------------------------------------------------------


@pytest.fixture(scope="function")
def client(db_session: Session):
    """Fixture to create a FastAPI TestClient.

    This fixture provides a `TestClient` instance for making requests to the
    FastAPI application during tests. It overrides the `get_db` dependency
    to use the isolated test database session (`db_session`).
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# --- User and Token Fixtures ---------------------------------------------------

TEST_USER_PASSWORD = "testpassword123"
TEST_ADMIN_PASSWORD = "adminpassword123"


@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """Fixture to create a standard test user (doctor role).

    This fixture creates a new user with the role of "doctor" in the test
    database and returns the corresponding `User` ORM object.
    """
    unique_email = f"test_{str(uuid.uuid4()).replace('-', '')}@example.com"
    user_in = UserCreate(email=unique_email, password=TEST_USER_PASSWORD, role="doctor")
    return user_crud.create_user(db_session, user_in)


@pytest.fixture(scope="function")
def test_admin_user(db_session: Session) -> User:
    """Fixture to create an admin test user.

    This fixture creates a new user with the role of "admin" in the test
    database and returns the corresponding `User` ORM object.
    """
    unique_email = f"admin_{str(uuid.uuid4()).replace('-', '')}@example.com"
    user_in = UserCreate(email=unique_email, password=TEST_ADMIN_PASSWORD, role="admin")
    return user_crud.create_user(db_session, user_in)


@pytest.fixture(scope="function")
def test_token(test_user: User) -> str:
    """Fixture to create a JWT access token for the standard test user."""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture(scope="function")
def test_admin_token(test_admin_user: User) -> str:
    """Fixture to create a JWT access token for the admin test user."""
    return create_access_token(data={"sub": test_admin_user.email})


def get_token(client: TestClient, email: str, password: str) -> str:
    """Helper function to obtain a JWT token from the login endpoint.

    This function makes a request to the `/login/access-token` endpoint with
    the provided credentials and returns the access token.
    """
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    return response.json()["access_token"]
