"""model_version.py

This file defines the SQLAlchemy ORM model for `ModelVersion`.
It represents a record of a federated learning model version in the database,
including its unique identifier, version number, performance metrics (accuracy, loss),
creation timestamp, description, and the file path to its stored weights.

Purpose:
- To define the database schema for tracking different versions of the FL model.
- To provide an ORM (Object-Relational Mapping) representation of model versions
  for easy interaction with the database.
- To enable persistent storage of model metadata and facilitate model management
  and deployment.

Key Components:
- `ModelVersion` class: Defines the database table structure and column types.
- `Base`: The declarative base class from SQLAlchemy, which all ORM models inherit from.
- SQLAlchemy `Column` types: Specify the data type and constraints for each attribute.
- `UUID` (from `sqlalchemy.dialects.postgresql`): Used for generating UUID primary keys.
- `func.now()`: Used for automatically setting the `created_at` timestamp.
"""

import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from ..db.base_class import Base


class ModelVersion(Base):
    """SQLAlchemy ORM model representing a version of the federated learning model in the database.

    This table stores metadata for each trained model version, including its unique
    identifier, a sequential version number, performance metrics, and a reference
    to where the model weights are stored.

    Attributes:
        __tablename__ (str): The name of the database table for this model.
        id (uuid.UUID): The primary key of the `model_versions` table. It's a UUID
                        (Universally Unique Identifier), automatically generated upon creation.
                        `as_uuid=True` ensures it's handled as a Python `uuid.UUID` object.
        version_number (int): A sequential integer representing the version of the model.
                              `nullable=False` and `unique=True` ensure each version number is distinct.
                              Indexed for efficient lookups.
        created_at (DateTime): The timestamp when this model version record was created.
                               `timezone=True` indicates timezone awareness. `server_default=func.now()`
                               sets the default value to the current server time upon insertion.
        avg_accuracy (float): The average accuracy achieved by this model version.
                              `nullable=True` allows for cases where accuracy might not be available.
        avg_loss (float): The average loss value of this model version.
                          `nullable=True` allows for cases where loss might not be available.
        description (str): An optional text field for a human-readable description of the model version,
                           e.g., details about the training run or specific features.
        file_path (str): The file path or URL where the actual model weights (e.g., a `.pth` file)
                         for this version are stored. `nullable=False` ensures this is always present.

    """

    __tablename__ = "model_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_number = Column(Integer, nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    avg_accuracy = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
