# -*- coding: utf-8 -*-
"""test_reports.py

This file contains tests for the reports and analysis-related endpoints.
It verifies the functionality of creating and retrieving reports, fetching
federated learning metrics, and triggering background tasks like FL rounds
and heatmap generation.

Purpose:
- To ensure that analysis reports can be created and retrieved correctly.
- To test the retrieval of FL metrics and report statistics.
- To verify that background tasks for FL and XAI can be triggered successfully.
- To ensure proper authorization for accessing different report-related endpoints.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend import crud, schemas
from backend.models.fl_metrics import FLRoundMetric
from backend.models.report import ReportStatus
from backend.models.user import User

from backend.tests.conftest import TEST_ADMIN_PASSWORD, TEST_USER_PASSWORD, get_token


def test_create_analysis_report(
    client: TestClient, db_session, test_admin_user, test_admin_token
):
    """Test creating a new analysis report."""
    # user_in = UserCreate(email="testuser@example.com", password=TEST_USER_PASSWORD, role="doctor")
    # test_user = create_user(db_session, user=user_in)
    # token = get_token(client, test_user.email, TEST_USER_PASSWORD)
    response = client.post(
        "/api/v1/reports/",
        json={
            "model_version": "v1.0",
            "status": "PENDING",
            "final_confidence_score": 0.85,
            "diagnosis_result": "Benign",
            "image_count": 10,
        },
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["model_version"] == "v1.0"
    assert response.json()["diagnosis_result"] == "Benign"
    assert response.json()["image_count"] == 10


def test_read_reports(
    client: TestClient, db_session, test_admin_user: User, test_admin_token: str
):
    """Test reading a list of reports."""
    # Create a report first
    crud.report.create_report(
        db_session,
        schemas.ReportCreate(
            model_version="v1.0",
            status=ReportStatus.COMPLETED,
            final_confidence_score=0.8,
            diagnosis_result="Malignant",
            image_count=10,
        ),
        owner_id=test_admin_user.id,
    )
    db_session.commit()
    response = client.get(
        "/api/v1/reports/", headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["model_version"] == "v1.0"


def test_read_fl_metrics(client: TestClient, db_session):
    """Test reading federated learning metrics."""
    from backend.crud.user import create_user
    from backend.schemas.user import UserCreate

    user_in = UserCreate(
        email="testuser@example.com", password=TEST_USER_PASSWORD, role="doctor"
    )
    test_user = create_user(db_session, user=user_in)
    token = get_token(client, test_user.email, TEST_USER_PASSWORD)
    # Add a dummy FLRoundMetric
    metric = FLRoundMetric(
        round_number=1,
        avg_accuracy=0.85,
        avg_loss=0.15,
        num_clients=5,
        avg_uncertainty=0.0,
    )
    db_session.add(metric)
    db_session.commit()
    db_session.refresh(metric)

    response = client.get(
        "/api/v1/reports/fl-metrics", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["round_number"] == 1


def test_start_fl_round(client: TestClient, db_session):
    """Test starting a new federated learning round (admin only)."""
    from backend.crud.user import create_user
    from backend.schemas.user import UserCreate

    user_in = UserCreate(
        email="admin@example.com", password=TEST_ADMIN_PASSWORD, role="admin"
    )
    test_admin_user = create_user(db_session, user=user_in)
    token = get_token(client, test_admin_user.email, TEST_ADMIN_PASSWORD)
    response = client.post(
        "/api/v1/reports/start-fl-round", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert (
        response.json()["message"]
        == "Federated learning round initiation request received."
    )


def test_trigger_heatmap_generation(client: TestClient, db_session, test_user: User):
    """Test triggering heatmap generation for a report."""
    from backend.crud.user import create_user
    from backend.schemas.user import UserCreate

    user_in = UserCreate(
        email="testuser@example.com", password=TEST_USER_PASSWORD, role="doctor"
    )
    test_user = create_user(db_session, user=user_in)
    token = get_token(client, test_user.email, TEST_USER_PASSWORD)

    # Create a report to generate a heatmap for
    report = crud.report.create_report(
        db_session,
        schemas.ReportCreate(
            model_version="v1.0",
            status=ReportStatus.COMPLETED,
            final_confidence_score=0.9,
            diagnosis_result="Benign",
            image_count=5,
        ),
        owner_id=test_user.id,
    )
    db_session.commit()

    # Mock the Celery task
    with patch("backend.worker.generate_heatmap_task") as mock_task:
        mock_task.delay.return_value.id = "mock_task_id"
        response = client.post(
            f"/api/v1/reports/{report.id}/generate-heatmap",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Heatmap generation started."
        assert response.json()["task_id"] == "mock_task_id"
        mock_task.delay.assert_called_once_with(str(report.id))


def test_get_report_statistics(
    client: TestClient, db_session, test_admin_user, test_admin_token
):
    """Test retrieving aggregated statistics about reports."""
    # user_in = UserCreate(email="testuser@example.com", password=TEST_USER_PASSWORD, role="doctor")
    # test_user = create_user(db_session, user=user_in)
    # token = get_token(client, test_user.email, TEST_USER_PASSWORD)

    # Create some reports with different statuses and data
    crud.report.create_report(
        db_session,
        schemas.ReportCreate(
            model_version="v1.0",
            status=ReportStatus.COMPLETED,
            final_confidence_score=0.9,
            diagnosis_result="Benign",
            image_count=5,
        ),
        owner_id=test_admin_user.id,
    )
    crud.report.create_report(
        db_session,
        schemas.ReportCreate(
            model_version="v1.1",
            status=ReportStatus.COMPLETED,
            final_confidence_score=0.8,
            diagnosis_result="Malignant",
            image_count=10,
        ),
        owner_id=test_admin_user.id,
    )
    crud.report.create_report(
        db_session,
        schemas.ReportCreate(
            model_version="v1.2",
            status=ReportStatus.PENDING,
            final_confidence_score=None,
            diagnosis_result=None,
            image_count=3,
        ),
        owner_id=test_admin_user.id,
    )
    crud.report.create_report(
        db_session,
        schemas.ReportCreate(
            model_version="v1.3",
            status=ReportStatus.FAILED,
            final_confidence_score=None,
            diagnosis_result=None,
            image_count=7,
        ),
        owner_id=test_admin_user.id,
    )
    db_session.commit()

    response = client.get(
        "/api/v1/reports/statistics",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )

    assert response.status_code == 200
    stats = response.json()

    assert stats["total_reports"] >= 4
    assert stats["completed_reports"] >= 2
    assert stats["pending_reports"] >= 1
    assert stats["failed_reports"] >= 1
    assert pytest.approx(stats["avg_confidence_score"]) == 0.85  # (0.9 + 0.8) / 2
    assert stats["diagnosis_distribution"] == {"Benign": 1, "Malignant": 1}
    assert pytest.approx(stats["avg_images_per_report"]) == 6.25  # (5 + 10 + 3 + 7) / 4
