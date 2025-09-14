# -*- coding: utf-8 -*-
"""model_versions.py

This file defines the API endpoints for managing federated learning model versions.
It provides functionality to retrieve lists of all model versions and details of
specific model versions. Access to these endpoints is restricted to administrators,
ensuring that sensitive model information is only accessible to authorized personnel.

Purpose:
- To provide a secure interface for administrators to track and manage trained
  federated learning models.
- To enable retrieval of model metadata, such as version number, accuracy, loss,
  and file path.
- To enforce role-based access control for model version information.

Key Components:
- `APIRouter`: Organizes model version-related endpoints.
- `crud.model_version`: Database interaction layer for model version models.
- `schemas`: Pydantic models for request and response data validation.
- `backend.core.security.get_current_admin_user`: Dependency to ensure only
  authenticated admin users can access these endpoints.
"""

from typing import List

from .. import crud, schemas
from ..core.exceptions import ResourceNotFoundException
from ..core.security import has_permission
from ..db.session import get_db
from ..models.user import Permission, User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[schemas.ModelVersion])
def read_model_versions(
    db: Session = Depends(get_db),  # Database session dependency.
    skip: int = 0,  # Query parameter for pagination: number of records to skip.
    limit: int = 100,  # Query parameter for pagination: maximum number of records to return.
    current_user: User = Depends(
        has_permission(Permission.VIEW_MODEL_VERSIONS)
    ),  # Dependency to ensure only admin users can access.
):
    """Retrieve all model versions (requires VIEW_MODEL_VERSIONS permission).

    This endpoint allows authenticated users with `VIEW_MODEL_VERSIONS` permission
    to retrieve a paginated list of all federated learning model versions stored in the system. It provides
    an overview of the trained models and their associated metadata.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip for pagination. Defaults to 0.
        limit (int): The maximum number of records to return for pagination. Defaults to 100.
        current_user (User): The authenticated user object, ensuring access control.

    Returns:
        List[schemas.ModelVersion]: A list of model version objects, each conforming
                                    to the `schemas.ModelVersion` Pydantic model.

    Raises:
        HTTPException: If the user does not have the required permission.

    """
    model_versions = crud.model_version.get_multi(db, skip=skip, limit=limit)
    return model_versions


@router.get("/{version_id}", response_model=schemas.ModelVersion)
def read_model_version(
    version_id: str,  # Path parameter: The unique identifier of the model version.
    db: Session = Depends(get_db),  # Database session dependency.
    current_user: User = Depends(
        has_permission(Permission.VIEW_MODEL_VERSIONS)
    ),  # Dependency to ensure only admin users can access.
):
    """Retrieve a specific model version by ID (requires VIEW_MODEL_VERSIONS permission).

    This endpoint allows authenticated users with `VIEW_MODEL_VERSIONS` permission
    to retrieve detailed information about a specific federated learning model version using its unique ID.

    Args:
        version_id (str): The unique identifier (ID) of the model version to retrieve.
        db (Session): The SQLAlchemy database session.
        current_user (User): The authenticated user object, ensuring access control.

    Returns:
        schemas.ModelVersion: The model version object, conforming to `schemas.ModelVersion`.

    Raises:
        HTTPException:
            - 404 Not Found: If the `version_id` does not correspond to an existing model version.
            - 403 Forbidden: If the user does not have the required permission.

    """
    model_version = crud.model_version.get(db, id=version_id)
    if not model_version:
        raise ResourceNotFoundException(detail="Model version not found.")
    return model_version
