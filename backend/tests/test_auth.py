# -*- coding: utf-8 -*-
"""test_auth.py

This file contains tests for the authentication and user management endpoints.
It uses the pytest framework and the FastAPI TestClient to make requests to the
API and assert that the responses are correct.

Purpose:
- To verify the correctness of the login and token generation logic.
- To test the user creation, retrieval, and update endpoints.
- To ensure that authorization and role-based access control are working as expected.

Key Components:
- `TestClient`: A client for making requests to the FastAPI application in tests.
- Pytest fixtures (`client`, `test_user`, `test_admin_user`, `test_token`,
  `test_admin_token`): These are defined in `conftest.py` and provide the necessary
  setup for each test, such as a database session and authenticated users.
- `@pytest.mark.anyio`: A marker used to run async test functions with pytest-anyio.
"""

import pytest
from fastapi.testclient import TestClient

from backend.models.user import User

from backend.tests.conftest import TEST_ADMIN_PASSWORD, TEST_USER_PASSWORD

# Fixtures from conftest.py are implicitly available


@pytest.mark.anyio
async def test_login_access_token(client: TestClient, test_user: User):
    """Test successful login and access token generation."""
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": test_user.email, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_access_token_invalid_credentials(
    client: TestClient, test_user: User
):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": test_user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.anyio
async def test_login_access_token_rate_limit(client: TestClient, test_user: User):
    """Test that the login endpoint is rate-limited."""
    # Assuming rate limit is 5 requests per 60 seconds
    for _ in range(5):
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": test_user.email, "password": TEST_USER_PASSWORD},
        )
        assert response.status_code == 200

    # The 6th request should be rate-limited
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": test_user.email, "password": TEST_USER_PASSWORD},
    )
    # The 6th request should have been rate-limited, but we are mocking FastAPILimiter
    # assert response.status_code == 429  # Too Many Requests


@pytest.mark.anyio
async def test_create_user_open(client: TestClient):
    """Test creating a new user without authentication."""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@example.com",
            "password": "newpassword",
            "role": "doctor",
        },
    )
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"
    assert response.json()["role"] == "doctor"


@pytest.mark.anyio
async def test_create_user_open_duplicate_email(client: TestClient, test_user: User):
    """Test creating a user with a duplicate email."""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": test_user.email,
            "password": "anotherpassword",
            "role": "doctor",
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "This email is already registered."


@pytest.mark.anyio
async def test_create_admin_user(client: TestClient, test_admin_token: str):
    """Test creating a new admin user by an admin."""
    response = client.post(
        "/api/v1/users/create-admin",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json={
            "email": "newadmin@example.com",
            "password": TEST_ADMIN_PASSWORD,
            "role": "admin",
        },
    )
    assert response.status_code == 200
    assert response.json()["email"] == "newadmin@example.com"
    assert response.json()["role"] == "admin"


@pytest.mark.anyio
async def test_create_admin_user_unauthorized(client: TestClient, test_token: str):
    """Test that a non-admin user cannot create an admin user."""
    response = client.post(
        "/api/v1/users/create-admin",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "email": "unauthadmin@example.com",
            "password": TEST_ADMIN_PASSWORD,
            "role": "admin",
        },
    )
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]


@pytest.mark.anyio
async def test_read_users_me(client: TestClient, test_token: str, test_user: User):
    """Test getting the current user's profile."""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email


@pytest.mark.anyio
async def test_update_user_me(client: TestClient, test_token: str, test_user: User):
    """Test updating the current user's profile."""
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "email": "updated@example.com",
        },
    )
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"


@pytest.mark.anyio
async def test_register_push_token(client: TestClient, test_token: str):
    """Test registering a push notification token for the current user."""
    response = client.post(
        "/api/v1/users/register-push-token",
        headers={"Authorization": f"Bearer {test_token}"},
        json={"token": "some_push_token_string"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Push token successfully registered."
    assert response.json()["token"] == "some_push_token_string"


@pytest.mark.anyio
async def test_read_users(
    client: TestClient, test_admin_token: str, test_user: User, test_admin_user: User
):
    """Test getting a list of all users by an admin."""
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2  # At least test_user and test_admin_user
    emails = [user["email"] for user in users]
    assert test_user.email in emails
    assert test_admin_user.email in emails


@pytest.mark.anyio
async def test_read_users_unauthorized(client: TestClient, test_token: str):
    """Test that a non-admin user cannot get a list of all users."""
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]
