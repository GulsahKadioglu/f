"""medical_image.py

This file provides the Create, Read, Update, Delete (CRUD) operations for the
`MedicalImage` database model. It encapsulates the logic for interacting with
the database specifically for medical image records, ensuring proper association
with their parent medical cases.

Purpose:
- To abstract database interactions for medical images from the API layer.
- To provide functions for creating new medical image records, linking them to
  an existing medical case.

Key Components:
- `MedicalImage`: The SQLAlchemy ORM model representing a medical image in the database.
- `MedicalImageCreate`: Pydantic schema for validating input data when creating a new medical image.
- `Session`: SQLAlchemy database session for performing database operations.
"""

import uuid
from typing import List, TypeVar

from sqlalchemy.orm import Session

from ..models.medical_image import MedicalImage
from ..schemas.medical_image import MedicalImageCreate, MedicalImageUpdate

ModelType = TypeVar("ModelType", bound=MedicalImage)


def create_with_case(
    db: Session, *, obj_in: MedicalImageCreate, case_id: uuid.UUID
) -> MedicalImage:
    """Creates a new medical image record in the database, associating it with a specific medical case.

    This function takes the input data for a new medical image (primarily its file path)
    and the UUID of the medical case it belongs to. It constructs a `MedicalImage` ORM object,
    adds it to the session, commits the transaction, and refreshes the object to load
    any database-generated fields.

    Args:
        db (Session): The SQLAlchemy database session.
        obj_in (MedicalImageCreate): A Pydantic schema object containing the data
                                    for the new medical image (e.g., `image_path`).
        case_id (uuid.UUID): The UUID of the `MedicalCase` to which this image belongs.

    Returns:
        MedicalImage: The newly created `MedicalImage` ORM object, as it exists in the database.

    """
    db_obj = MedicalImage(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get(db: Session, id: uuid.UUID) -> MedicalImage | None:
    """Retrieves a single medical image record by its unique identifier.

    Args:
        db (Session): The database session.
        id (uuid.UUID): The UUID of the MedicalImage to retrieve.

    Returns:
        MedicalImage | None: The MedicalImage object if found, else None.

    """
    return db.query(MedicalImage).filter(MedicalImage.id == id).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[MedicalImage]:
    """Retrieves a list of MedicalImage records with pagination.

    Args:
        db (Session): The database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to retrieve.

    Returns:
        List[MedicalImage]: A list of MedicalImage objects.

    """
    return db.query(MedicalImage).offset(skip).limit(limit).all()


def update(
    db: Session, *, db_obj: MedicalImage, obj_in: MedicalImageUpdate | dict
) -> MedicalImage:
    """Updates an existing MedicalImage record.

    Args:
        db (Session): The database session.
        db_obj (MedicalImage): The existing MedicalImage object from the database.
        obj_in (MedicalImageUpdate | dict): Pydantic model or dictionary with the updated data.

    Returns:
        MedicalImage: The updated MedicalImage object.

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


def remove(db: Session, *, id: uuid.UUID) -> MedicalImage | None:
    """Removes a MedicalImage record by its ID.

    Args:
        db (Session): The database session.
        id (uuid.UUID): The ID of the MedicalImage to remove.

    Returns:
        MedicalImage | None: The removed MedicalImage object if found and deleted, else None.

    """
    obj = db.query(MedicalImage).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
