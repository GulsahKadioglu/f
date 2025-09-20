# -*- coding: utf-8 -*-
"""base_class.py

This file defines the declarative base for all SQLAlchemy ORM models in the
application. It creates a `Base` class that all other models will inherit from.

Purpose:
- To provide a common, centralized base class for all ORM models.
- To act as a registry for all mapped classes, which is essential for
  SQLAlchemy's metadata management and for tools like Alembic to detect
  database schema changes.

Key Components:
- `declarative_base`: A factory function from SQLAlchemy that constructs the
  base class.
- `Base`: The instance of the declarative base that all models will inherit from.
"""

from sqlalchemy.orm import declarative_base

# Create the declarative base class.
# All SQLAlchemy ORM models in this application will inherit from this `Base`.
# This `Base` object acts as a catalog for the mapped classes and their table metadata.
Base = declarative_base()

# Import all models here to ensure they are registered with SQLAlchemy's metadata.
# This is a critical step for database table creation and migrations (e.g., using Alembic).
# When `Base.metadata.create_all(engine)` is called, SQLAlchemy uses this metadata
# to generate the DDL (Data Definition Language) for all defined tables.
# These imports are necessary for their side effects (registering with Base.metadata),
# even if the imported modules are not directly used in this file.
