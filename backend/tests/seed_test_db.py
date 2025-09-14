# -*- coding: utf-8 -*-
"""seed_test_db.py

This script is designed to be run before the e2e tests to seed the database
with a known test user.
"""

from sqlalchemy.orm import Session

from backend.crud.user import create_user
from backend.db.session import SessionLocal
from backend.models.user import User
from backend.schemas.user import UserCreate


def seed_test_user(db: Session):
    """Creates a test user if it doesn't exist."""
    test_user = db.query(User).filter(User.email == "test@example.com").first()
    if test_user:
        print(f"Test user 'test@example.com' already exists.")
        return

    print("Creating test user 'test@example.com'.")
    user_in = UserCreate(email="test@example.com", password="testpassword", role="admin")
    user = create_user(db, user=user_in)
    print(f"Test user '{user.email}' created successfully.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_test_user(db)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()