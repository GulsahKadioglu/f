"""session.py

This file is responsible for configuring and managing database connections
and SQLAlchemy sessions for the FastAPI application. It sets up the database
engine, defines a session factory, and provides a FastAPI dependency function
(`get_db`) to easily inject database sessions into API routes.

Purpose:
- To establish and manage the connection to the PostgreSQL database.
- To provide a consistent way to create and manage database sessions.
- To integrate database sessions seamlessly with FastAPI's dependency injection system.
- To ensure proper session lifecycle management (opening and closing sessions).

Key Components:
- `create_engine`: SQLAlchemy function to create the database engine.
- `sessionmaker`: SQLAlchemy function to create a configurable Session class.
- `SessionLocal`: The configured session class, used to create new database sessions.
- `get_db`: A FastAPI dependency generator function for providing database sessions.
"""

from backend.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency to get a database session.

    This function is a generator that yields a new database session for each
    request. It ensures that the session is always closed after the request
    is finished, even if an error occurs, by using a `try...finally` block.
    This pattern is crucial for proper resource management in web applications.

    Yields:
        Session: A new SQLAlchemy database session object.

    Usage:
        This function is typically used as a dependency in FastAPI route functions:
        `db: Session = Depends(get_db)`

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
