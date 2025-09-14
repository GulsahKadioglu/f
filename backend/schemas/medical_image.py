"""medical_image.py

This file defines Pydantic schemas for `MedicalImage`.
These schemas are used for data validation, serialization, and deserialization
of medical image data, ensuring data consistency when interacting with the API
and database.

Purpose:
- To define the structure and data types for medical image data.
- To validate incoming request data (e.g., when creating new image records).
- To serialize outgoing response data (e.g., when retrieving image details).
- To enable ORM mode (or `from_attributes`) for seamless conversion between
  Pydantic models and SQLAlchemy ORM objects.

Key Components:
- `MedicalImageBase`, `MedicalImageCreate`, `MedicalImageUpdate`:
  Schemas for managing medical image data at different stages (base, creation, update).
- `MedicalImageInDBBase`, `MedicalImage`: Schemas for representing image data as stored
  in the database and for full API responses.
- `BaseModel`: Pydantic's base class for creating data models.
- `model_config = ConfigDict(from_attributes=True)`: Enables Pydantic to work directly with SQLAlchemy ORM models (Pydantic v2).
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MedicalImageBase(BaseModel):
    """Base Pydantic schema for a medical image.

    This schema defines the common attributes that are typically provided when
    creating or updating a medical image record, excluding database-generated fields.

    Attributes:
        image_path (str): The file path or URL where the medical image is stored.
        image_type (Optional[str]): An optional field to categorize the type of image
                                    (e.g., "X-RAY", "MRI", "CT"). Defaults to `None`.
        case_id (int): The ID of the associated medical case. This is a foreign key.

    """

    image_path: str
    image_type: Optional[str] = None
    case_id: int
    # DICOM Metadata
    study_instance_uid: Optional[str] = None
    series_instance_uid: Optional[str] = None
    sop_instance_uid: Optional[str] = None
    modality: Optional[str] = None
    instance_number: Optional[int] = None


class MedicalImageCreate(MedicalImageBase):
    """Pydantic schema for creating a new medical image record.

    This schema inherits from `MedicalImageBase` and is used specifically for
    validating incoming data when a new medical image record is submitted to the API.
    It doesn't add any new fields but serves as a distinct type for clarity.
    """

    pass


class MedicalImageUpdate(MedicalImageBase):
    """Pydantic schema for updating an existing medical image record.

    This schema inherits from `MedicalImageBase` and is used for validating
    incoming data when updating an existing medical image record. All fields are
    marked as `Optional` to allow for partial updates (PATCH requests).
    """

    image_path: Optional[str] = None
    image_type: Optional[str] = None
    case_id: Optional[int] = None


class MedicalImage(MedicalImageBase):
    """Pydantic schema for a medical image, including database-generated fields.

    This schema extends `MedicalImageBase` and is typically used for responses
    when retrieving medical image details from the API. It serves as the full
    representation of a medical image record.
    """

    id: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicalImageResponse(MedicalImage):
    """Pydantic schema for the response when retrieving medical images.

    Includes the full URL for client-side access.
    """

    url: str
