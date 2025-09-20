# -*- coding: utf-8 -*-
"""deps.py

This file defines FastAPI dependencies that are used across multiple API
endpoints. Centralizing dependencies here helps to avoid code duplication
and makes them easily reusable.

Purpose:
- To provide a reliable way to obtain a database session for API endpoints.
- To re-export common authentication dependencies for easy access.

Key Components:
- `get_db`: A dependency that creates and yields a new SQLAlchemy `Session`
  for each request, ensuring that the session is always closed, even if
  errors occur.
- `get_current_user`, `get_current_active_user`: Re-exported from the
  `backend.core.security` module to provide a single point of import for
  authentication-related dependencies.
"""

from typing import Generator

from backend.core.security import get_current_active_user, get_current_user
from backend.db.session import SessionLocal
from backend.models.user import User
from fastapi import Depends


def get_db() -> Generator:
    """FastAPI dependency to provide a database session.

    This function is a generator that creates a new SQLAlchemy `SessionLocal`
    for each request that uses it as a dependency. It yields the session to the
    request handler and then ensures that the session is closed in a `finally`
    block. This pattern is crucial for proper database connection management.

    Yields:
        Generator: A generator that yields a SQLAlchemy `Session` object.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Re-exporting for easier access in other modules
__all__ = ["get_db", "get_current_user", "get_current_active_user", "User", "Depends"]