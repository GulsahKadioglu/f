"""medical_case.py

This file provides the Create, Read, Update, Delete (CRUD) operations for the
`MedicalCase` database model. It encapsulates the logic for interacting with
the database specifically for medical case records, ensuring data integrity
and proper association with their owners (doctors).

Purpose:
- To abstract database interactions for medical cases from the API layer.
- To provide functions for creating new medical cases, associating them with a doctor.
- To retrieve single or multiple medical cases, with options for filtering by owner
  and pagination.

Key Components:
- `MedicalCase`: The SQLAlchemy ORM model representing a medical case in the database.
- `MedicalCaseCreate`: Pydantic schema for validating input data when creating a new medical case.
- `Session`: SQLAlchemy database session for performing database operations.
"""

import uuid
from typing import List, Optional, TypeVar

from sqlalchemy.orm import Session, joinedload

from ..models.medical_image import MedicalImage
from ..schemas.medical_case import MedicalCaseCreate, MedicalCaseUpdate

from ..models.medical_case import MedicalCase

ModelType = TypeVar("ModelType", bound=MedicalCase)


def create_with_owner(
    db: Session, *, obj_in: MedicalCaseCreate, owner_id: uuid.UUID
) -> MedicalCase:
    """Creates a new medical case record in the database, associating it with a specific owner.

    This function takes the input data for a new medical case and the UUID of the
    doctor who owns this case. It constructs a `MedicalCase` ORM object, adds it
    to the session, commits the transaction, and refreshes the object to load
    any database-generated fields (like the ID).

    Args:
        db (Session): The SQLAlchemy database session.
        obj_in (MedicalCaseCreate): A Pydantic schema object containing the data
                                    for the new medical case (e.g., `patient_id`).
        owner_id (uuid.UUID): The UUID of the `User` (doctor) who is creating and owning this case.

    Returns:
        MedicalCase: The newly created `MedicalCase` ORM object, as it exists in the database.

    """
    generated_case_id = uuid.uuid4()
    db_obj = MedicalCase(
        case_id=generated_case_id, patient_id=obj_in.patient_id, doctor_id=owner_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_multi_by_owner(
    db: Session,
    *,
    owner_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
) -> List[MedicalCase]:
    """Retrieves a paginated list of medical cases owned by a specific user.

    This function queries the database for `MedicalCase` records that are associated
    with the given `owner_id`. It supports pagination through `skip` and `limit`
    parameters, allowing for efficient retrieval of large datasets.

    Args:
        db (Session): The SQLAlchemy database session.
        owner_id (uuid.UUID): The UUID of the `User` (doctor) whose medical cases are to be retrieved.
        skip (int): The number of records to skip (offset) for pagination. Defaults to 0.
        limit (int): The maximum number of records to return (limit) for pagination. Defaults to 100.
        status (Optional[str]): Filter cases by their status (e.g., "PENDING", "REVIEW").

    Returns:
        List[MedicalCase]: A list of `MedicalCase` ORM objects that belong to the specified owner.

    """
    query = (
        db.query(MedicalCase)
        .options(joinedload(MedicalCase.medical_images))
        .filter(MedicalCase.doctor_id == owner_id)
    )
    if status:
        query = query.filter(MedicalCase.status == status)
    return query.offset(skip).limit(limit).all()


def get_multi(
    db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None
) -> List[MedicalCase]:
    """Retrieves a paginated list of all medical cases.

    This function queries the database for all `MedicalCase` records. It supports
    pagination through `skip` and `limit` parameters, and can filter by status.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip (offset) for pagination. Defaults to 0.
        limit (int): The maximum number of records to return (limit) for pagination. Defaults to 100.
        status (Optional[str]): Filter cases by their status (e.g., "PENDING", "REVIEW").

    Returns:
        List[MedicalCase]: A list of `MedicalCase` ORM objects.

    """
    query = db.query(MedicalCase).options(joinedload(MedicalCase.medical_images))
    if status:
        query = query.filter(MedicalCase.status == status)
    return query.offset(skip).limit(limit).all()


def get(db: Session, id: uuid.UUID) -> MedicalCase | None:
    """Retrieves a single medical case record by its unique identifier.

    Args:
        db (Session): The SQLAlchemy database session.
        id (uuid.UUID): The UUID of the `MedicalCase` to retrieve.

    Returns:
        MedicalCase | None: The `MedicalCase` ORM object if found; otherwise, `None`.

    """
    return (
        db.query(MedicalCase)
        .options(joinedload(MedicalCase.medical_images))
        .filter(MedicalCase.case_id == id)
        .first()
    )

def get_by_id(db: Session, id: int) -> MedicalCase | None:
    """Retrieves a single medical case record by its integer ID.

    Args:
        db (Session): The SQLAlchemy database session.
        id (int): The integer ID of the `MedicalCase` to retrieve.

    Returns:
        MedicalCase | None: The `MedicalCase` ORM object if found; otherwise, `None`.

    """
    return (
        db.query(MedicalCase)
        .options(joinedload(MedicalCase.medical_images))
        .filter(MedicalCase.id == id)
        .first()
    )


def update(
    db: Session, *, db_obj: MedicalCase, obj_in: MedicalCaseUpdate | dict
) -> MedicalCase:
    """Updates an existing MedicalCase record.

    Args:
        db (Session): The database session.
        db_obj (MedicalCase): The existing MedicalCase object from the database.
        obj_in (MedicalCaseUpdate | dict): Pydantic model or dictionary with the updated data.

    Returns:
        MedicalCase: The updated MedicalCase object.

    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    for field in update_data:
        setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, id: uuid.UUID) -> MedicalCase | None:
    """Removes a MedicalCase record by its ID.

    Args:
        db (Session): The database session.
        id (uuid.UUID): The ID of the MedicalCase to remove.

    Returns:
        MedicalCase | None: The removed MedicalCase object if found and deleted, else None.

    """
    obj = db.query(MedicalCase).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj


def get_images_by_case(db: Session, *, case_id: uuid.UUID) -> List[MedicalImage]:
    """Retrieves all medical images associated with a specific medical case.

    Args:
        db (Session): The SQLAlchemy database session.
        case_id (uuid.UUID): The UUID of the `MedicalCase` whose images are to be retrieved.

    Returns:
        List[MedicalImage]: A list of `MedicalImage` ORM objects associated with the case.

    """
    return db.query(MedicalImage).join(MedicalCase).filter(MedicalCase.case_id == case_id).all()