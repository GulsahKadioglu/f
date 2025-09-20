# -*- coding: utf-8 -*-
"""test_medical_cases.py

This file contains tests for the medical case and medical image endpoints.
It verifies the functionality of creating medical cases, uploading images,
and retrieving case details, while also testing authorization and error handling.

Purpose:
- To ensure that medical cases can be created successfully.
- To test the uploading of valid DICOM images to a medical case.
- To verify that the system handles invalid file types correctly.
- To test the retrieval of medical case data and ensure proper authorization.
"""

import os
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Fixtures from conftest.py are implicitly available


def test_create_medical_case(client: TestClient, test_token: str):
    """Test creating a new medical case."""
    response = client.post(
        "/api/v1/medical-cases/",
        headers={"Authorization": f"Bearer {test_token}"},
        data={"patient_id": "PATIENT123"},
    )
    assert response.status_code == 200
    assert response.json()["patient_id"] == "PATIENT123"


def test_create_medical_case_invalid_patient_id(client: TestClient, test_token: str):
    """Test creating a medical case with an invalid patient ID."""
    response = client.post(
        "/api/v1/medical-cases/",
        headers={"Authorization": f"Bearer {test_token}"},
        data={"patient_id": "invalid-id!@#"},
    )
    assert response.status_code == 400


import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from io import BytesIO

def test_upload_medical_image(client: TestClient, test_token: str, db_session: Session):
    """Test uploading a valid medical image to a case."""
    # Create a case first
    case_response = client.post(
        "/api/v1/medical-cases/",
        headers={"Authorization": f"Bearer {test_token}"},
        data={"patient_id": "PATIENT456"},
    )
    assert case_response.status_code == 200
    case_id = case_response.json()["case_id"]

    # Create a dummy DICOM file
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.ExplicitVRLittleEndian
    file_meta.MediaStorageSOPInstanceUID = "1.2.3.4.5.6.7.8.9.10.11.12"
    file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
    ds = FileDataset("dummy.dcm", {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.PatientName = "Test^Patient"
    ds.StudyInstanceUID = "1.2.3.4.5.6.7.8.9.10"
    ds.SeriesInstanceUID = "1.2.3.4.5.6.7.8.9.10.11"
    ds.SOPInstanceUID = "1.2.3.4.5.6.7.8.9.10.11.12"
    ds.Modality = "CT"
    ds.InstanceNumber = 1
    ds.is_implicit_VR = True
    ds.is_little_endian = True

    buffer = BytesIO()
    pydicom.dcmwrite(buffer, ds)
    buffer.seek(0)

    response = client.post(
        f"/api/v1/medical-cases/{case_id}/images/",
        headers={"Authorization": f"Bearer {test_token}"},
        files={"file": ("test_dicom.dcm", buffer, "application/dicom")},
    )

    assert response.status_code == 200



def test_upload_medical_image_invalid_type(
    client: TestClient, test_token: str, db_session: Session
):
    """Test uploading an invalid file type to a medical case."""
    # Create a case first
    case_response = client.post(
        "/api/v1/medical-cases/",
        headers={"Authorization": f"Bearer {test_token}"},
        data={"patient_id": "PATIENT789"},
    )
    assert case_response.status_code == 200
    case_id = case_response.json()["case_id"]

    # Upload an invalid file type
    file_content = b"fake text content"
    with open("test_document.txt", "wb") as f:
        f.write(file_content)

    with open("test_document.txt", "rb") as f:
        response = client.post(
            f"/api/v1/medical-cases/{case_id}/images/",
            headers={"Authorization": f"Bearer {test_token}"},
            files={"file": ("test_document.txt", f, "text/plain")},
        )
    os.remove("test_document.txt")

    assert response.status_code == 400
    assert "Could not parse DICOM metadata" in response.json()["detail"]


def test_read_single_medical_case(
    client: TestClient, test_token: str, db_session: Session
):
    """Test reading a single medical case."""
    # Create a case first
    case_response = client.post(
        "/api/v1/medical-cases/",
        headers={"Authorization": f"Bearer {test_token}"},
        data={"patient_id": "PATIENT003"},
    )
    assert case_response.status_code == 200
    case_id = case_response.json()["case_id"]

    response = client.get(
        f"/api/v1/medical-cases/{case_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert response.status_code == 200


def test_read_medical_case_not_found(client: TestClient, test_token: str):
    """Test reading a medical case that does not exist."""
    non_existent_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/medical-cases/{non_existent_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert response.status_code == 404


def test_read_medical_case_unauthorized_access(
    client: TestClient, test_token: str, db_session: Session
):
    """Test that a user cannot access a medical case owned by another user."""
    # Create a case with a different user
    from backend.crud.user import create_user
    from backend.schemas.user import UserCreate

    from backend.tests.conftest import get_token

    user_in = UserCreate(
        email="other@example.com", password="otherpassword", role="doctor"
    )
    other_user = create_user(db_session, user=user_in)
    other_token = get_token(client, other_user.email, "otherpassword")

    case_response = client.post(
        "/api/v1/medical-cases/",
        headers={"Authorization": f"Bearer {other_token}"},
        data={"patient_id": "PATIENT004"},
    )
