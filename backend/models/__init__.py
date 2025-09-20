"""__init__.py (Models Package Initialization)

This file serves as the initialization file for the `models` package.
It imports all individual SQLAlchemy ORM models, making them accessible
from a single, convenient entry point (e.g., `from app.models import User`).

Purpose:
- To provide a centralized location for importing all database models.
- To simplify model imports in other parts of the application (e.g., CRUD operations, API schemas).
- To ensure that all models are registered with SQLAlchemy's metadata when this package is imported,
  which is crucial for database schema generation and migrations.

Key Components:
- Imports individual model classes (e.g., `User`, `AnalysisReport`, `FLRoundMetric`,
  `MedicalCase`, `MedicalImage`, `ModelVersion`).
"""

from .fl_metrics import FLRoundMetric
from .medical_case import MedicalCase
from .medical_image import MedicalImage
from .model_version import ModelVersion
from .report import AnalysisReport
from .user import User