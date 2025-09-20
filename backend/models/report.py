"""report.py

This file defines the SQLAlchemy ORM model for `AnalysisReport`.
It represents a record of an analysis report in the database, including its
unique identifier, creation timestamp, the model version used for analysis,
its current status, and a final confidence score.

Purpose:
- To define the database schema for storing analysis report information.
- To provide an ORM (Object-Relational Mapping) representation of analysis reports
  for easy interaction with the database.
- To track the lifecycle and results of medical analysis processes.

Key Components:
- `ReportStatus` enum: Defines the possible states of an analysis report.
- `AnalysisReport` class: Defines the database table structure and column types.
- `Base`: The declarative base class from SQLAlchemy, which all ORM models inherit from.
- SQLAlchemy `Column` types: Specify the data type and constraints for each attribute.
- `UUID` (from `sqlalchemy.dialects.postgresql`): Used for generating UUID primary keys.
- `datetime.datetime.utcnow`: Used for automatically setting the `created_at` timestamp.
"""

import enum
import uuid

from sqlalchemy import (  # Added Integer
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from backend.db.base_class import Base


class ReportStatus(str, enum.Enum):
    """An enumeration defining the possible states or statuses of an analysis report.

    This enum ensures that the `status` field in the `AnalysisReport` model
    can only take on predefined, valid values, improving data consistency
    and clarity regarding the report's lifecycle.

    Values:
        PENDING (str): The report has been created but processing has not yet started.
        PROCESSING (str): The report is currently being analyzed or processed.
        COMPLETED (str): The analysis for the report has finished successfully.
        FAILED (str): The analysis for the report failed due to an error.
    """

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AnalysisReport(Base):
    """SQLAlchemy ORM model representing an analysis report in the database.

    This table stores the results and metadata of a medical analysis, linking
    it to the model version used and tracking its processing status.

    Attributes:
        __tablename__ (str): The name of the database table for this model.
        id (uuid.UUID): The primary key of the `analysis_reports` table. It's a UUID,
                        automatically generated upon creation. `as_uuid=True` ensures
                        it's handled as a Python `uuid.UUID` object.
        created_at (DateTime): The timestamp when this analysis report record was created.
                               `default=datetime.datetime.utcnow` sets the default value to
                               the current UTC time upon insertion.
        model_version (str): A string identifying the version of the machine learning model
                             that was used to generate this analysis report. `nullable=False`.
        status (ReportStatus): The current processing status of the report, using the `ReportStatus` enum.
                               Defaults to `ReportStatus.PENDING`.
        final_confidence_score (float): An optional floating-point number representing the
                                        confidence score of the analysis result. `nullable=True`
                                        as it might not be available until processing is complete.

    """

    __tablename__ = "analysis_reports"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, server_default=func.now())
    model_version = Column(String, nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    final_confidence_score = Column(Float, nullable=True)
    diagnosis_result = Column(String, nullable=True)  # e.g., "Benign", "Malignant"
    image_count = Column(
        Integer, nullable=True
    )  # Number of images analyzed for this report
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
