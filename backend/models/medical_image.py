"""medical_image.py

This file defines the SQLAlchemy ORM model for `MedicalImage`.
It represents a record of a medical image in the database, storing its file path,
image type, and a foreign key reference to the `MedicalCase` it belongs to.

Purpose:
- To define the database schema for storing metadata about medical images.
- To provide an ORM (Object-Relational Mapping) representation of medical images
  for easy interaction with the database.
- To establish a many-to-one relationship with the `MedicalCase` model.

Key Components:
- `MedicalImage` class: Defines the database table structure and column types.
- `Base`: The declarative base class from SQLAlchemy, which all ORM models inherit from.
- SQLAlchemy `Column` types: Specify the data type and constraints for each attribute.
- `ForeignKey`: Defines the relationship to the `medical_cases` table.
- `relationship`: Defines the many-to-one relationship with `MedicalCase`.
- `func.now()`: Used for automatically setting the `uploaded_at` timestamp.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base_class import Base


class MedicalImage(Base):
    """SQLAlchemy ORM model representing a medical image record in the database.

    This table stores metadata about medical images, primarily their storage path
    and a link to the medical case they are part of. It does not store the image
    binary data directly, but rather a reference to it.

    Attributes:
        __tablename__ (str): The name of the database table for this model.
        id (int): The primary key of the `medical_images` table. Auto-incrementing integer.
        image_path (str): The file path or URL where the medical image is securely stored.
                          `nullable=False` ensures this field is always present.
        image_type (str): An optional field to categorize the type of image (e.g., "X-RAY", "MRI", "CT").
                          This can be used for filtering or specific processing.
        case_id (int): A foreign key linking to the `medical_cases` table. This establishes
                       the relationship between an image and its parent medical case.
        uploaded_at (DateTime): The timestamp when the image record was created (i.e., when it was uploaded).
                                `timezone=True` indicates timezone awareness. `server_default=func.now()`
                                sets the default value to the current server time upon insertion.
        medical_case (relationship): Defines a many-to-one relationship with the `MedicalCase` model.
                                     `back_populates="medical_images"` establishes a bidirectional relationship,
                                     allowing access to associated images from a `MedicalCase` object.

    """

    __tablename__ = "medical_images"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    image_type = Column(String)
    # DICOM Metadata
    study_instance_uid = Column(String, index=True)
    series_instance_uid = Column(String, index=True)
    sop_instance_uid = Column(String, unique=True, index=True)
    modality = Column(String)
    instance_number = Column(Integer)

    case_id = Column(Integer, ForeignKey("medical_cases.id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    medical_case = relationship("MedicalCase", back_populates="medical_images")

    __table_args__ = ()
