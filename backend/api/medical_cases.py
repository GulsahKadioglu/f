# -*- coding: utf-8 -*-
"""medical_cases.py

This file defines the API endpoints for managing medical cases and their associated
medical images within the Federated Cancer Screening application. It provides
functionality for creating new cases, uploading images to existing cases, and
retrieving case details, ensuring proper authentication and authorization.

Purpose:
- To provide a secure interface for doctors to manage their patients' medical cases.
- To handle the secure upload and storage of sensitive medical images.
- To allow retrieval of medical case information, restricted to the case owner.

Key Components:
- `APIRouter`: Organizes medical case-related endpoints.
- `crud.medical_case` and `crud.medical_image`: Database interaction layers for
  medical case and image models.
- `schemas`: Pydantic models for request and response data validation.
- `backend.core.security.get_current_active_user`: Dependency to ensure authenticated
  and active users.
- Secure file storage mechanism for uploaded images.
"""

import re
import uuid
from pathlib import Path
from typing import List, Optional  # Added Optional and List

from .. import crud, schemas
from ..core.config import settings
from ..core.exceptions import (
    BadRequestException,
    PermissionDeniedException,
    ResourceNotFoundException,
)
from ..core.security import has_permission
from ..db.session import get_db
from ..models.medical_case import MedicalCase
from ..models.user import Permission, User, UserRole
from ..schemas.medical_image import MedicalImageResponse
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile  # Added Query
from sqlalchemy.orm import Session

router = APIRouter()

SECURE_STORAGE_PATH = Path(settings.MEDICAL_IMAGES_STORAGE_PATH)
SECURE_STORAGE_PATH.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=schemas.MedicalCase)
def create_case(
    *,
    db: Session = Depends(get_db),  # Database session dependency.
    patient_id: str = Form(...),  # Patient ID, received as form data.
    current_user: User = Depends(
        has_permission(Permission.CASE_MANAGE)
    ),  # Authenticated user dependency.
) -> MedicalCase:
    """Create a new medical case.

    This endpoint allows an authenticated user (doctor) to create a new medical case.
    A medical case is associated with a `patient_id` and the `doctor_id` of the
    creating user. This ensures that only the owning doctor can manage the case.

    Args:
        db (Session): The SQLAlchemy database session.
        patient_id (str): A unique identifier for the patient associated with this case.
                          Received as form data, which is suitable for simple string inputs.
        current_user (User): The authenticated user object, injected by the `get_current_active_user`
                             dependency. This user will be set as the owner of the medical case.

    Returns:
        MedicalCase: The newly created medical case object, conforming to `schemas.MedicalCase`.

    Raises:
        BadRequestException: If the patient_id format is invalid.

    """
    if not re.fullmatch(r"^[a-zA-Z0-9]{5,50}$", patient_id):
        raise BadRequestException(
            detail="Patient ID must be alphanumeric and between 5 and 50 characters long."
        )

    case_in = schemas.MedicalCaseCreate(patient_id=patient_id)
    case = crud.medical_case.create_with_owner(
        db=db, obj_in=case_in, owner_id=current_user.id
    )
    return case


@router.get("/", response_model=List[schemas.MedicalCase])
def get_all_cases(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),  # Added status filter
    current_user: User = Depends(has_permission(Permission.CASE_MANAGE)),
):
    """Retrieve a list of medical cases.

    Allows filtering by patient_id and status. Only cases owned by the current user (or all for admin) are returned.
    """
    if current_user.role == UserRole.ADMIN:
        cases = crud.medical_case.get_multi(db, skip=skip, limit=limit, status=status)
    else:
        cases = crud.medical_case.get_multi_by_owner(
            db, owner_id=current_user.id, skip=skip, limit=limit, status=status
        )

    if patient_id:
        cases = [case for case in cases if case.patient_id == patient_id]

    return cases


@router.get("/{case_id}", response_model=schemas.MedicalCase)
def get_case_by_id(
    *,
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission(Permission.CASE_VIEW_OWN)),
) -> MedicalCase:
    """Retrieve a single medical case by its ID.

    This endpoint allows an authenticated user to retrieve details of a specific medical case
    by providing its unique ID. Access is restricted to the owner of the case or an admin user.

    Args:
        case_id (uuid.UUID): The unique identifier of the medical case to retrieve.
        db (Session): The SQLAlchemy database session.
        current_user (User): The authenticated user object.

    Returns:
        MedicalCase: The retrieved medical case object.

    Raises:
        ResourceNotFoundException: If no medical case with the given ID is found.
        PermissionDeniedException: If the current user is not authorized to view the case.

    """
    case = crud.medical_case.get(db, id=case_id)
    if not case:
        raise ResourceNotFoundException(detail="Medical case not found.")

    # Check if the user is the owner or an admin
    if case.doctor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise PermissionDeniedException(
            detail="Not authorized to view this medical case."
        )

    return case


from io import BytesIO

import pydicom

# ... (rest of the imports)


from ..encryption_service import encrypt_file_content, decrypt_file_content
from starlette.responses import StreamingResponse
from starlette.background import BackgroundTask
import mimetypes

@router.post("/{case_id}/images", response_model=schemas.MedicalImage)
async def upload_medical_image(
    *,
    case_id: uuid.UUID,  # Path parameter: UUID of the medical case to associate the image with.
    db: Session = Depends(get_db),  # Database session dependency.
    current_user: User = Depends(
        has_permission(Permission.CASE_MANAGE)
    ),  # Authenticated user dependency.
    file: UploadFile = File(...),  # Uploaded file, expected to be an image.
):
    # Validate case existence and user permission
    case = crud.medical_case.get(db, id=case_id)
    if not case:
        raise ResourceNotFoundException(detail="Medical case not found.")
    if case.doctor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise PermissionDeniedException(
            detail="Not authorized to upload images to this medical case."
        )

    # Read file content into memory for parsing
    file_content = await file.read()
    await file.seek(0)  # Reset file pointer after reading

    # --- DICOM Metadata Extraction ---
    try:
        # Use a BytesIO object to allow pydicom to read the in-memory file content
        dicom_dataset = pydicom.dcmread(BytesIO(file_content), force=True)

        # Extract metadata
        study_instance_uid = str(dicom_dataset.StudyInstanceUID)
        series_instance_uid = str(dicom_dataset.SeriesInstanceUID)
        sop_instance_uid = str(dicom_dataset.SOPInstanceUID)
        modality = str(dicom_dataset.Modality)
        instance_number = int(dicom_dataset.InstanceNumber)

    except Exception as e:
        raise BadRequestException(detail=f"Could not parse DICOM metadata: {e}")

    # --- End of Extraction ---

    # Encrypt the file content
    encrypted_content = encrypt_file_content(file_content)

    # Save the encrypted file securely
    file_extension = Path(file.filename).suffix or ".dcm"
    # Use SOPInstanceUID for a unique, stable filename for the encrypted file
    safe_filename = f"{sop_instance_uid}.enc"  # Add .enc extension to indicate encryption
    file_path = SECURE_STORAGE_PATH / safe_filename

    try:
        with file_path.open("wb") as buffer:
            buffer.write(encrypted_content)
    finally:
        await file.close()

    # Create Medical Image Record with extracted metadata
    image_in = schemas.MedicalImageCreate(
        image_path=str(file_path),  # Store path to encrypted file
        case_id=case.id,
        study_instance_uid=study_instance_uid,
        series_instance_uid=series_instance_uid,
        sop_instance_uid=sop_instance_uid,
        modality=modality,
        instance_number=instance_number,
    )
    return crud.medical_image.create_with_case(db, obj_in=image_in, case_id=case.id)


@router.get("/images/{image_id}/download", tags=["medical_images"])
async def download_medical_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission(Permission.CASE_VIEW_OWN)),
):
    """
    Downloads a medical image by its ID, decrypting it on the fly.
    Requires authentication and appropriate permissions.
    """
    medical_image = crud.medical_image.get(db, id=image_id)
    if not medical_image:
        raise ResourceNotFoundException(detail="Medical image not found.")

    # Check if the user has permission to view the associated case
    case = crud.medical_case.get_by_id(db, id=medical_image.case_id)
    if not case: # Should not happen if medical_image exists and has a case_id
        raise ResourceNotFoundException(detail="Associated medical case not found.")
    if case.doctor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise PermissionDeniedException(
            detail="Not authorized to download this medical image."
        )

    encrypted_file_path = Path(medical_image.image_path)

    if not encrypted_file_path.exists():
        raise ResourceNotFoundException(detail="Encrypted image file not found on server.")

    try:
        with encrypted_file_path.open("rb") as f:
            encrypted_content = f.read()
        decrypted_content = decrypt_file_content(encrypted_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decrypting file: {e}")

    # Determine content type based on original file extension (assuming .dcm for DICOM)
    # If original extension is not available, default to application/octet-stream
    content_type, _ = mimetypes.guess_type(medical_image.image_path.replace(".enc", ""))
    if not content_type:
        content_type = "application/dicom" # Default for DICOM files

    # Clean up temporary file if created (not needed here as we use BytesIO)
    def cleanup():
        pass # No temporary file to clean up, content is in memory

    return StreamingResponse(
        BytesIO(decrypted_content),
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{medical_image.sop_instance_uid}.dcm\""
        },
        background=BackgroundTask(cleanup)
    )


from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    Request,
    UploadFile,
)  # Added Request
from starlette.datastructures import URL

# ... (rest of the imports)

# ... (rest of the file)


@router.get("/{case_id}/images", response_model=List[MedicalImageResponse])
def get_medical_images_for_case(
    *,
    case_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_permission(Permission.CASE_VIEW_OWN)),
):
    """Retrieve all medical images for a specific case, returning full URLs and metadata.
    """
    case = crud.medical_case.get(db, id=case_id)
    if not case:
        raise ResourceNotFoundException(detail="Case not found")
    if case.doctor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise PermissionDeniedException(
            detail="Not authorized to view images for this case"
        )

    images = crud.medical_case.get_images_by_case(db, case_id=case_id)

    response_data = []
    for image in images:
        # Generate secure download URL for the encrypted image
        download_url = request.url.replace(
            path=f"/api/v1/medical-cases/images/{image.id}/download"
        )

        image_response = MedicalImageResponse(
            **image.__dict__, url=str(download_url)
        )
        response_data.append(image_response)

    return response_data
