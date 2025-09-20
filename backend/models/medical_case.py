"""medical_case.py

This file defines the SQLAlchemy ORM model for `MedicalCase`.
It represents a medical case record in the database, including patient information,
case status, and timestamps. It also establishes relationships with associated
medical images.

Purpose:
- To define the database schema for storing medical case information.
- To provide an ORM (Object-Relational Mapping) representation of medical cases
  for easy interaction with the database.
- To establish relationships with other related models, such as `MedicalImage`.

Key Components:
- `MedicalCase` class: Defines the database table structure and column types.
- `Base`: The declarative base class from SQLAlchemy, which all ORM models inherit from.
- SQLAlchemy `Column` types: Specify the data type and constraints for each attribute.
- `relationship`: Defines the one-to-many relationship with `MedicalImage`.
- `func.now()`: Used for automatically setting timestamps upon creation and update.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from backend.db.types import GUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.base_class import Base


class MedicalCase(Base):
    """SQLAlchemy ORM model representing a medical case in the database.

    This table stores core information about a medical case, including a patient
    identifier, the case status, and timestamps for creation and last update.
    It also links to the `User` model (doctor) who owns the case and to `MedicalImage`
    records associated with it.

    Attributes:
        __tablename__ (str): The name of the database table for this model.
        id (int): The primary key of the `medical_cases` table. Auto-incrementing integer.
        case_id (str): A unique identifier for the medical case, often a UUID.
                       Indexed for efficient lookups. `nullable=False` ensures it's always present.
        patient_id (str): An identifier for the patient associated with this case.
                          Indexed for efficient lookups. `nullable=False`.
        status (str): The current status of the medical case (e.g., "PENDING", "REVIEW", "COMPLETED").
                      Defaults to "PENDING". `nullable=False`.
        created_at (DateTime): The timestamp when the medical case record was created.
                               `timezone=True` indicates timezone awareness. `server_default=func.now()`
                               sets the default value to
                               the current server time.
        updated_at (DateTime): The timestamp when the medical case record was last updated.
                               `timezone=True` indicates timezone awareness. `onupdate=func.now()`
                               automatically updates this field to the current server time on any record update.
        doctor_id (UUID): Foreign key linking to the `User` table, representing the doctor
                          who owns this medical case. `nullable=False`.
        medical_images (relationship): Defines a one-to-many relationship with the `MedicalImage` model.
                                       `back_populates="medical_case"` establishes a bidirectional relationship.
                                       `cascade="all, delete-orphan"` ensures that if a medical case is deleted,
                                       all associated medical images are also deleted.

    """

    __tablename__ = "medical_cases"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(GUID, unique=True, index=True, nullable=False)
    patient_id = Column(String, index=True, nullable=False)
    status = Column(String, default="PENDING", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    doctor_id = Column(GUID, ForeignKey("users.id"), nullable=False)

    # Relationships
    medical_images = relationship(
        "models.medical_image.MedicalImage", back_populates="medical_case", cascade="all, delete-orphan"
    )

    __table_args__ = {'extend_existing': True}