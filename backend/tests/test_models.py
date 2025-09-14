# -*- coding: utf-8 -*-
"""test_models.py

This file contains tests for the SQLAlchemy database models.
It verifies that the models can be created, committed to the database, and
that their relationships are correctly established.

Purpose:
- To ensure the integrity and correctness of the database schema as defined
  by the SQLAlchemy ORM models.
- To test the creation of individual model instances and their relationships.
"""

import uuid  # Added import for uuid

import pytest
from sqlalchemy.orm import Session

from backend.models.fl_metrics import FLRoundMetric
from backend.models.medical_case import MedicalCase
from backend.models.medical_image import MedicalImage
from backend.models.model_version import ModelVersion
from backend.models.report import AnalysisReport, ReportStatus
from backend.models.user import User, UserRole


@pytest.fixture(
    autouse=True
)  # Use autouse to ensure models are mapped for all tests in this file
def setup_models_for_tests(db_session: Session):
    """Fixture to ensure all models are loaded before tests in this file run.

    This fixture is used to explicitly reference all SQLAlchemy models. While
    `conftest.py` handles the table creation, this ensures that the models
    are loaded into SQLAlchemy's metadata registry before the tests are executed.
    """
    # Ensure all models are mapped before creating tables
    # This is typically handled by Base.metadata.create_all in conftest.py
    # but explicitly referencing them here ensures they are loaded.
    User.__table__
    AnalysisReport.__table__
    MedicalCase.__table__
    MedicalImage.__table__
    ModelVersion.__table__
    FLRoundMetric.__table__
    # No need to create_all or drop_all here, conftest handles it.


def test_models_can_be_created_and_related(db_session: Session):
    """Tests the creation and relationships of various database models.
    This includes User, MedicalCase, MedicalImage, AnalysisReport, and FLRoundMetric.
    """
    # Test creating a User
    new_user = User(
        email="test_user@example.com",
        hashed_password="hashed_password",
        role=UserRole.DOCTOR,
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    assert new_user.id is not None

    # Test creating a MedicalCase related to the User
    new_case = MedicalCase(patient_id="patient123", case_id=uuid.uuid4())
    new_case.doctor_id = new_user.id  # Assign doctor_id after creation
    db_session.add(new_case)
    db_session.commit()
    db_session.refresh(new_case)
    assert new_case.id is not None
    assert new_case.doctor_id == new_user.id

    # Test creating a MedicalImage related to the MedicalCase
    new_image = MedicalImage(image_path="/path/to/image.png", case_id=new_case.id)
    db_session.add(new_image)
    db_session.commit()
    db_session.refresh(new_image)
    assert new_image.id is not None
    assert new_image.case_id == new_case.id

    # Test creating an AnalysisReport
    new_report = AnalysisReport(
        model_version="v1.0",
        status=ReportStatus.COMPLETED,
        final_confidence_score=0.95,
        doctor_id=new_user.id,
    )
    db_session.add(new_report)
    db_session.commit()
    db_session.refresh(new_report)
    assert new_report.id is not None
    assert new_report.doctor_id == new_user.id

    # Test creating an FLRoundMetric
    new_metric = FLRoundMetric(
        round_number=1, avg_accuracy=0.85, avg_loss=0.15, num_clients=5
    )
    db_session.add(new_metric)
    db_session.commit()
    db_session.refresh(new_metric)
    assert new_metric.id is not None
