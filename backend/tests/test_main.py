# -*- coding: utf-8 -*-
"""test_main.py

This file contains a collection of integration tests for the main application API.
It tests various endpoints, including user creation, login, and retrieval of
federated learning metrics.

Purpose:
- To provide end-to-end tests for key API functionalities.
- To ensure that user authentication and authorization are working correctly.
- To verify the behavior of the federated learning metrics endpoints.
"""

from fastapi.testclient import TestClient

from backend.models.fl_metrics import FLRoundMetric

from backend.tests.conftest import TEST_ADMIN_PASSWORD, TEST_USER_PASSWORD, get_token

# Testler


def test_create_user(client: TestClient):
    """Test creating a new user."""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@example.com",
            "password": "testpassword123",
            "role": "doctor",
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"


def test_login_for_access_token(client: TestClient, db_session):
    """Test logging in to get an access token."""
    from backend.crud.user import create_user
    from backend.schemas.user import UserCreate

    user_in = UserCreate(
        email="testuser@example.com", password=TEST_USER_PASSWORD, role="doctor"
    )
    test_user = create_user(db_session, user=user_in)
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": test_user.email, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_read_users_me(client: TestClient, db_session):
    """Test reading the current user's profile."""
    from backend.crud.user import create_user
    from backend.schemas.user import UserCreate

    user_in = UserCreate(
        email="testuser@example.com", password=TEST_USER_PASSWORD, role="doctor"
    )
    test_user = create_user(db_session, user=user_in)
    token = get_token(client, test_user.email, TEST_USER_PASSWORD)

    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email


def test_update_user_me(client: TestClient, db_session):
    """Test updating the current user's profile."""
    from backend.crud.user import create_user
    from backend.schemas.user import UserCreate

    user_in = UserCreate(
        email="testuser@example.com", password=TEST_USER_PASSWORD, role="doctor"
    )
    test_user = create_user(db_session, user=user_in)
    token = get_token(client, test_user.email, TEST_USER_PASSWORD)

    response = client.put(
        "/api/v1/users/me",
        json={
            "email": "updated@example.com",
            "password": "newpassword",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"


def test_read_users_admin(client: TestClient, db_session):
    """Test reading all users as an admin."""
    from backend.crud.user import create_user
    from backend.schemas.user import UserCreate

    user_in = UserCreate(
        email="admin@example.com", password=TEST_ADMIN_PASSWORD, role="admin"
    )
    test_admin_user = create_user(db_session, user=user_in)
    token = get_token(client, test_admin_user.email, TEST_ADMIN_PASSWORD)

    response = client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["email"] == test_admin_user.email


def test_read_users_non_admin(client: TestClient, db_session):
    """Test reading all users as a non-admin user (should be forbidden)."""
    from backend.crud.user import create_user
    from backend.schemas.user import UserCreate

    user_in = UserCreate(
        email="testuser@example.com", password=TEST_USER_PASSWORD, role="doctor"
    )
    test_user = create_user(db_session, user=user_in)
    token = get_token(client, test_user.email, TEST_USER_PASSWORD)

    response = client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403  # Forbidden


def test_get_latest_fl_metrics_success(
    client: TestClient, test_admin_token: str, db_session
):
    """Test successfully retrieving the latest FL metrics."""
    # Create a dummy FL metric in the database
    fl_metric = FLRoundMetric(
        round_number=1,
        avg_accuracy=0.85,
        avg_loss=0.15,
        num_clients=5,
        avg_uncertainty=0.0,
    )
    db_session.add(fl_metric)
    db_session.commit()
    db_session.refresh(fl_metric)

    response = client.get(
        "/api/v1/fl/metrics/latest",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["round_number"] == 1
    assert response.json()["avg_accuracy"] == 0.85


def test_get_latest_fl_metrics_not_found(client: TestClient, test_admin_token: str):
    """Test retrieving the latest FL metrics when none exist."""
    response = client.get(
        "/api/v1/fl/metrics/latest",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "No FL metrics found."
