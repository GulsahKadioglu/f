# -*- coding: utf-8 -*-
"""medical_case.py

This file defines Pydantic schemas for `MedicalCase` and `MedicalImage`.
These schemas are used for data validation, serialization, and deserialization
of medical case and image data, ensuring data consistency when interacting
with the API and database.

Purpose:
- To define the structure and data types for medical case and image data.
- To validate incoming request data (e.g., when creating new cases or uploading images).
- To serialize outgoing response data (e.g., when retrieving case details).
- To enable ORM mode for seamless conversion between Pydantic models and SQLAlchemy ORM objects.

Key Components:
- `MedicalCaseBase`, `MedicalCaseCreate`, `MedicalCaseUpdate`, `MedicalCase`:
  Schemas for managing medical case data at different stages (base, creation, update, full).
- `MedicalImage`, `MedicalImageCreate`: Schemas for managing medical image data.
- `BaseModel`: Pydantic's base class for creating data models.
- `model_config = ConfigDict(from_attributes=True)`: Enables Pydantic to work directly with SQLAlchemy ORM models (Pydantic v2).
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MedicalCaseBase(BaseModel):
    """Base Pydantic schema for a medical case.

    This schema defines the common attributes that are typically present in a medical case
    and are used for both creation and retrieval, excluding database-generated fields.

    Attributes:
        patient_id (str): A unique identifier for the patient associated with the medical case.

    """

    patient_id: str


class MedicalCaseCreate(MedicalCaseBase):
    """Pydantic schema for creating a new medical case.

    This schema inherits from `MedicalCaseBase` and is used specifically for
    validating incoming data when a new medical case is submitted to the API.
    It doesn't add any new fields but serves as a distinct type for clarity.
    """

    pass


class MedicalCaseUpdate(MedicalCaseBase):
    """Pydantic schema for updating an existing medical case.

    This schema inherits from `MedicalCaseBase` and is used for validating
    incoming data when updating an existing medical case. All fields are
    marked as `Optional` to allow for partial updates (PATCH requests).

    Attributes:
        patient_id (Optional[str]): The updated patient ID. Optional, allowing for updates
                                    to other fields without changing the patient ID.
        status (Optional[str]): The updated status of the case.

    """

    patient_id: Optional[str] = None
    status: Optional[str] = None  # Added status field


class MedicalImage(BaseModel):
    """Pydantic schema for a medical image record.

    This schema represents the data structure for a medical image as it would be
    returned from the API, including its unique ID, storage path, and upload timestamp.

    Attributes:
        id (uuid.UUID): The unique identifier of the medical image record.
        image_path (str): The file path or URL where the medical image is stored.
        upload_timestamp (datetime): The timestamp when the image record was created.

    """

    id: uuid.UUID
    image_path: str
    upload_timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicalCase(MedicalCaseBase):
    """Pydantic schema for a medical case, including its relationships.

    This schema extends `MedicalCaseBase` by adding database-generated fields
    and including a list of associated `MedicalImage` records. It is used for
    full representation of a medical case in API responses.

    Attributes:
        id (int): The integer primary key of the medical case.
        case_id (uuid.UUID): The unique identifier of the medical case.
        case_date (datetime): The date and time when the medical case was created.
                              This is an alias for the `created_at` field in the ORM model.
        doctor_id (uuid.UUID): The unique identifier of the doctor who owns this case.
        status (str): The current status of the case (e.g., PENDING, REVIEWED).
        images (List[MedicalImage]): A list of `MedicalImage` schemas associated with this case.
                                     Defaults to an empty list if no images are present.

    """

    id: int
    case_id: uuid.UUID
    case_date: datetime = Field(alias="created_at") # Alias for created_at
    doctor_id: uuid.UUID
    status: str
    images: List[MedicalImage] = []

    model_config = ConfigDict(from_attributes=True)


class MedicalImageCreate(BaseModel):
    """Pydantic schema for creating a new medical image record.

    This schema defines the required fields when submitting data to create a new
    medical image record. It primarily includes the path where the image file
    is or will be stored.

    Attributes:
        image_path (str): The file path or URL where the medical image is stored.

    """

    image_path: str
