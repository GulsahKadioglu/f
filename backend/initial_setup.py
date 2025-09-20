# -*- coding: utf-8 -*-
"""initial_setup.py

This script is designed to be run once to perform the initial setup of the
application, specifically to create the first administrative user. It ensures
that the application has at least one admin account to start with.

Purpose:
- To create an initial admin user in the database.
- To prevent the creation of duplicate admin users if one already exists.
- To be run as a standalone script from the command line.

Usage:
    python -m backend.initial_setup
"""

from sqlalchemy.orm import Session

from backend.crud.user import create_user
from backend.db.session import SessionLocal
from backend.models.user import User
from backend.schemas.user import UserCreate


def create_initial_admin(db: Session):
    """Creates an initial admin user if no admin user exists in the database.

    This function checks if an admin user is already present in the database.
    If not, it prompts the user to enter an email and password for the new
    admin account and then creates the user.

    Args:
        db (Session): The SQLAlchemy database session.
    """
    # Check if an admin user already exists.
    admin_user = db.query(User).filter(User.role == "admin").first()
    if admin_user:
        print(
            f"Admin user '{admin_user.email}' already exists. "
            f"Skipping initial admin creation."
        )
        return

    # If no admin user exists, prompt for details and create one.
    print("No admin user found. Creating initial admin user.")
    admin_email = input("Enter initial admin email: ")
    admin_password = input("Enter initial admin password: ")

    user_in = UserCreate(email=admin_email, password=admin_password, role="admin")
    user = create_user(db, user=user_in)
    print(f"Admin user '{user.email}' created successfully.")


# This block ensures that the script can be run directly.
if __name__ == "__main__":
    # Create a new database session.
    db = SessionLocal()
    try:
        # Attempt to create the initial admin user.
        create_initial_admin(db)
    except Exception as e:
        # Print any errors that occur during the process.
        print(f"An error occurred: {e}")
    finally:
        # Always close the database session to release the connection.
        db.close()