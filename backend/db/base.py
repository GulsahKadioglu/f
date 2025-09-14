# -*- coding: utf-8 -*-
"""base.py

This file serves as a central point for importing all the database models and the
SQLAlchemy `Base` class. By importing all model classes here, we ensure that
they are registered with the `Base.metadata` object before any database
operations (like table creation with Alembic) are attempted.

Purpose:
- To ensure all SQLAlchemy ORM models are registered with the declarative base.
- To provide a single, convenient module from which to import all models.

Usage:
This module is typically imported when setting up the database or running
migrations to make sure all tables are known to SQLAlchemy.
"""

# Import the Base class from base_class.py. The `# noqa` comment is used to
# suppress linting errors about the import not being used directly in this file.
# Its side effect (registering the Base class) is what's important.
from .base_class import Base  # noqa

# Import all the models. Similar to the Base import, these are imported for their
# side effect of registering themselves with the `Base.metadata`.
from ..models.user import User  # noqa
from ..models.medical_case import MedicalCase  # noqa
from ..models.medical_image import MedicalImage  # noqa
from ..models.report import AnalysisReport  # noqa
from ..models.model_version import ModelVersion  # noqa
from ..models.fl_metrics import FLRoundMetric  # noqa