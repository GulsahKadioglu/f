# -*- coding: utf-8 -*-
"""test_fl.py

This file contains tests for the federated learning (FL) related endpoints.
It verifies the functionality of retrieving the encryption context, creating,
and managing FL metrics.

Purpose:
- To ensure that the FL context can be retrieved by authenticated users.
- To test the creation of FL metrics and ensure it is restricted to admin users.
- To verify the retrieval of all, latest, and specific FL metrics.
- To test the deletion and updating of FL metrics by admin users.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.crud.fl_metric import create as create_fl_metric_crud
from backend.models.user import User
from backend.schemas.fl_metric import FLRoundMetricBase

from .conftest import TEST_USER_PASSWORD, get_token


def test_get_fl_context(client: TestClient, test_token: str):
    """Test retrieving the FL encryption context."""
    response = client.get(
        "/api/v1/fl/context", headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert "context" in response.json()
    assert isinstance(response.json()["context"], str)


def test_create_fl_metric(
    client: TestClient,
    db_session: Session,
    test_admin_user: User,
    test_admin_token: str,
):
    """Test creating an FL metric by an admin and verify permission for non-admin."""
    fl_metric_data = {
        "round_number": 1,
        "avg_accuracy": 0.85,
        "avg_loss": 0.15,
        "num_clients": 5,
        "avg_uncertainty": 0.0,
    }
    response = client.post(
        "/api/v1/fl/metrics",
        json=fl_metric_data,
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["round_number"] == 1
    assert response.json()["avg_accuracy"] == 0.85

    # Verify permission denied for non-admin
    from backend.crud.user import create_user
    from backend.schemas.user import UserCreate

    user_in = UserCreate(
        email="testuser@example.com", password=TEST_USER_PASSWORD, role="doctor"
    )
    test_user = create_user(db_session, user=user_in)
    test_user_token = get_token(client, test_user.email, TEST_USER_PASSWORD)

    response = client.post(
        "/api/v1/fl/metrics",
        json=fl_metric_data,
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 403


def test_get_all_fl_metrics(
    client: TestClient, db_session: Session, test_admin_token: str
):
    """Test retrieving all FL metrics."""
    create_fl_metric_crud(
        db_session,
        obj_in=FLRoundMetricBase(
            round_number=1,
            avg_accuracy=0.8,
            avg_loss=0.2,
            num_clients=3,
            avg_uncertainty=0.0,
        ),
    )
    create_fl_metric_crud(
        db_session,
        obj_in=FLRoundMetricBase(
            round_number=2,
            avg_accuracy=0.85,
            avg_loss=0.15,
            num_clients=5,
            avg_uncertainty=0.0,
        ),
    )
    db_session.commit()

    response = client.get(
        "/api/v1/fl/metrics", headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 2
    assert response.json()[0]["round_number"] == 1


def test_get_latest_fl_metric(
    client: TestClient, db_session: Session, test_admin_token: str
):
    """Test retrieving the latest FL metric."""
    create_fl_metric_crud(
        db_session,
        obj_in=FLRoundMetricBase(
            round_number=1,
            avg_accuracy=0.8,
            avg_loss=0.2,
            num_clients=3,
            avg_uncertainty=0.0,
        ),
    )
    create_fl_metric_crud(
        db_session,
        obj_in=FLRoundMetricBase(
            round_number=2,
            avg_accuracy=0.85,
            avg_loss=0.15,
            num_clients=5,
            avg_uncertainty=0.0,
        ),
    )
    db_session.commit()

    response = client.get(
        "/api/v1/fl/metrics/latest",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["round_number"] == 2


def test_get_fl_metric_by_round(
    client: TestClient, db_session: Session, test_admin_token: str
):
    """Test retrieving an FL metric by its round number."""
    create_fl_metric_crud(
        db_session,
        obj_in=FLRoundMetricBase(
            round_number=10,
            avg_accuracy=0.9,
            avg_loss=0.1,
            num_clients=10,
            avg_uncertainty=0.0,
        ),
    )
    db_session.commit()

    response = client.get(
        "/api/v1/fl/metrics/round/10",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["round_number"] == 10

    response = client.get(
        "/api/v1/fl/metrics/round/999",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 404


def test_delete_fl_metric(
    client: TestClient, db_session: Session, test_admin_token: str
):
    """Test deleting an FL metric."""
    metric = create_fl_metric_crud(
        db_session,
        obj_in=FLRoundMetricBase(
            round_number=1,
            avg_accuracy=0.8,
            avg_loss=0.2,
            num_clients=3,
            avg_uncertainty=0.0,
        ),
    )
    db_session.commit()

    response = client.delete(
        f"/api/v1/fl/metrics/{metric.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 204

    response = client.get(
        f"/api/v1/fl/metrics/round/{metric.round_number}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 404


def test_update_fl_metric(
    client: TestClient, db_session: Session, test_admin_token: str
):
    """Test updating an FL metric."""
    metric = create_fl_metric_crud(
        db_session,
        obj_in=FLRoundMetricBase(
            round_number=1,
            avg_accuracy=0.8,
            avg_loss=0.2,
            num_clients=3,
            avg_uncertainty=0.0,
        ),
    )
    db_session.commit()

    update_data = {"avg_accuracy": 0.95, "num_clients": 7}
    response = client.put(
        f"/api/v1/fl/metrics/{metric.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["avg_accuracy"] == 0.95
    assert response.json()["num_clients"] == 7

    response = client.get(
        f"/api/v1/fl/metrics/round/{metric.round_number}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["avg_accuracy"] == 0.95
