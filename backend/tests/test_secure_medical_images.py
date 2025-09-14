# -*- coding: utf-8 -*-
"""test_secure_medical_images.py

This file contains tests for the secure medical image handling endpoints.
It verifies the functionality of uploading, downloading, and managing access
to encrypted medical images.

Purpose:
- To ensure that medical images are correctly encrypted upon upload and
  decrypted upon download.
- To test the authorization logic for accessing medical images.
- To verify error handling for invalid or non-existent images.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db.base_class import Base
from backend.core.config import settings
from backend.models.user import User, UserRole, Permission
from backend.models.medical_case import MedicalCase
from backend.models.medical_image import MedicalImage
from backend.core.security import create_access_token
from backend.core.hashing import get_password_hash
from datetime import timedelta
import uuid
from io import BytesIO
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pathlib import Path
import os
import shutil

# Setup test database
TEST_DATABASE_URL = "sqlite:///./test_secure_medical_images.db"

@pytest.fixture(scope="function")
def app_mocker(mocker):
    """Fixture to provide the mocker object."""
    return mocker

@pytest.fixture(scope="function")
def test_app(app_mocker):
    """Fixture to create a test application instance with a test database."""
    # Create a test engine and session local for SQLite
    test_engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Patch the engine and SessionLocal in backend.db.session
    app_mocker.patch("backend.db.session.engine", test_engine)
    app_mocker.patch("backend.db.session.SessionLocal", TestSessionLocal)

    # Import app after patching
    from backend.main import app
    from backend.db.session import get_db

    Base.metadata.create_all(bind=test_engine)

    # Override get_db dependency for testing
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    db_file_path = TEST_DATABASE_URL.replace("sqlite:///./", "")
    if os.path.exists(db_file_path):
        os.remove(db_file_path)

@pytest.fixture(scope="function")
def db_session(test_app):
    """Fixture to provide a database session for a test."""
    from backend.db.session import get_db
    session = next(get_db())
    yield session
    session.close()

@pytest.fixture(scope="function")
def client(test_app):
    """Fixture to provide a test client for the application."""
    yield test_app

@pytest.fixture(scope="function")
def admin_user(db_session):
    """Fixture to create an admin user in the test database."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("password"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def doctor_user(db_session):
    """Fixture to create a doctor user in the test database."""
    user = User(
        email="doctor@example.com",
        hashed_password=get_password_hash("password"),
        role=UserRole.DOCTOR,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def doctor_user_token(doctor_user):
    """Fixture to create an access token for the doctor user."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": doctor_user.email}, expires_delta=access_token_expires
    )

@pytest.fixture(scope="function")
def admin_user_token(admin_user):
    """Fixture to create an access token for the admin user."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": admin_user.email}, expires_delta=access_token_expires
    )

@pytest.fixture(scope="function")
def medical_case(db_session, doctor_user):
    """Fixture to create a medical case in the test database."""
    case = MedicalCase(
        case_id=uuid.uuid4(),
        patient_id="PATIENT123",
        doctor_id=doctor_user.id
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)
    return case

@pytest.fixture(scope="function")
def dummy_dicom_file():
    """Fixture to create a dummy DICOM file in memory."""
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
    return buffer

@pytest.fixture(autouse=True)
def cleanup_secure_storage():
    """Fixture to clean up the secure storage directory before and after tests."""
    SECURE_STORAGE_PATH = Path(settings.MEDICAL_IMAGES_STORAGE_PATH)
    SECURE_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    for item in SECURE_STORAGE_PATH.iterdir():
        if item.is_file():
            os.remove(item)
        elif item.is_dir():
            shutil.rmtree(item)
    yield
    for item in SECURE_STORAGE_PATH.iterdir():
        if item.is_file():
            os.remove(item)
        elif item.is_dir():
            shutil.rmtree(item)

def test_upload_and_download_medical_image(client, db_session, doctor_user_token, medical_case, dummy_dicom_file):
    """Test uploading and downloading a medical image."""
    response = client.post(
        f"/api/v1/medical-cases/{medical_case.case_id}/images",
        headers={"Authorization": f"Bearer {doctor_user_token}"},
        files={"file": ("test_dicom.dcm", dummy_dicom_file.read(), "application/dicom")}
    )
    assert response.status_code == 200, response.text
    uploaded_image = response.json()
    assert uploaded_image["sop_instance_uid"] == "1.2.3.4.5.6.7.8.9.10.11.12"
    assert uploaded_image["image_path"].endswith(".enc")

    encrypted_file_path = Path(uploaded_image["image_path"])
    assert encrypted_file_path.exists()
    with open(encrypted_file_path, "rb") as f:
        encrypted_content = f.read()
    from backend.encryption_service import decrypt_file_content
    decrypted_content = decrypt_file_content(encrypted_content)
    dummy_dicom_file.seek(0)
    assert decrypted_content == dummy_dicom_file.read()

    response = client.get(
        f"/api/v1/medical-cases/{medical_case.case_id}/images",
        headers={"Authorization": f"Bearer {doctor_user_token}"}
    )
    assert response.status_code == 200, response.text
    images_list = response.json()
    assert len(images_list) == 1
    download_url = images_list[0]["url"]
    assert f"/api/v1/medical-cases/images/{uploaded_image['id']}/download" in download_url

    response = client.get(
        download_url,
        headers={"Authorization": f"Bearer {doctor_user_token}"}
    )
    assert response.status_code == 200, response.text
    downloaded_content = response.content

    try:
        downloaded_dicom = pydicom.dcmread(BytesIO(downloaded_content), force=True)
        assert downloaded_dicom.SOPInstanceUID == "1.2.3.4.5.6.7.8.9.10.11.12"
        assert downloaded_dicom.PatientName == "Test^Patient"
    except Exception as e:
        pytest.fail(f"Downloaded content is not a valid DICOM file: {e}")

def test_download_unauthorized(client, db_session, medical_case, dummy_dicom_file, doctor_user_token):
    """Test that a user cannot download an image they don't have access to."""
    response = client.post(
        f"/api/v1/medical-cases/{medical_case.case_id}/images",
        headers={"Authorization": f"Bearer {doctor_user_token}"},
        files={"file": ("test_dicom.dcm", dummy_dicom_file.read(), "application/dicom")}
    )
    assert response.status_code == 200
    uploaded_image = response.json()

    response = client.get(f"/api/v1/medical-cases/images/{uploaded_image['id']}/download")
    assert response.status_code == 401

    other_doctor = User(
        email="other_doctor@example.com",
        hashed_password=get_password_hash("password"),
        role=UserRole.DOCTOR,
        is_active=True,
    )
    db_session.add(other_doctor)
    db_session.commit()
    db_session.refresh(other_doctor)
    other_doctor_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    other_doctor_token = create_access_token(
        data={"sub": other_doctor.email}, expires_delta=other_doctor_token_expires
    )

    response = client.get(
        f"/api/v1/medical-cases/images/{uploaded_image['id']}/download",
        headers={"Authorization": f"Bearer {other_doctor_token}"}
    )
    assert response.status_code == 403

def test_download_non_existent_image(client, doctor_user_token):
    """Test downloading a non-existent image."""
    non_existent_id = 12345
    response = client.get(
        f"/api/v1/medical-cases/images/{non_existent_id}/download",
        headers={"Authorization": f"Bearer {doctor_user_token}"}
    )
    assert response.status_code == 404

def test_upload_invalid_dicom(client, doctor_user_token, medical_case):
    """Test uploading an invalid DICOM file."""
    invalid_content = b"this is not a dicom file"
    response = client.post(
        f"/api/v1/medical-cases/{medical_case.case_id}/images",
        headers={"Authorization": f"Bearer {doctor_user_token}"},
        files={"file": ("invalid.dcm", invalid_content, "application/dicom")}
    )
    assert response.status_code == 400

def test_upload_no_permission(client, db_session, medical_case, dummy_dicom_file):
    """Test that a user cannot upload an image to a case they don't own."""
    no_permission_user = User(
        email="nopermission@example.com",
        hashed_password=get_password_hash("password"),
        role=UserRole.DOCTOR,
        is_active=True,
    )
    db_session.add(no_permission_user)
    db_session.commit()
    db_session.refresh(no_permission_user)
    no_permission_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    no_permission_token = create_access_token(
        data={"sub": no_permission_user.email}, expires_delta=no_permission_token_expires
    )

    response = client.post(
        f"/api/v1/medical-cases/{medical_case.case_id}/images",
        headers={"Authorization": f"Bearer {no_permission_token}"},
        files={"file": ("test_dicom.dcm", dummy_dicom_file.read(), "application/dicom")}
    )
    assert response.status_code == 403

def test_download_file_not_found_on_disk(client, db_session, doctor_user_token, medical_case):
    """Test downloading an image that is in the database but not on disk."""
    image_id = uuid.uuid4()
    image = MedicalImage(
        image_path=str(Path(settings.MEDICAL_IMAGES_STORAGE_PATH) / f"{image_id}.enc"),
        case_id=medical_case.id,
        study_instance_uid="1.2.3",
        series_instance_uid="4.5.6",
        sop_instance_uid="7.8.9",
        modality="MR",
        instance_number=1
    )
    db_session.add(image)
    db_session.commit()
    db_session.refresh(image)

    response = client.get(
        f"/api/v1/medical-cases/images/{image.id}/download",
        headers={"Authorization": f"Bearer {doctor_user_token}"}
    )
    assert response.status_code == 404
