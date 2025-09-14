"""user.py

This file provides the Create, Read, Update, Delete (CRUD) operations for the
`User` database model. It encapsulates the logic for interacting with the
database specifically for user records, including password hashing and
managing push notification tokens.

Purpose:
- To abstract database interactions for user management from the API layer.
- To provide functions for creating, retrieving, and updating user accounts.
- To ensure secure storage of user passwords by hashing them before saving.
- To manage user-specific data like push notification tokens.

Key Components:
- `User`: The SQLAlchemy ORM model representing a user in the database.
- `UserCreate`, `UserUpdate`: Pydantic schemas for validating input data during
  user creation and update operations.
- `Session`: SQLAlchemy database session for performing database operations.
- `get_password_hash`: Utility function for hashing passwords.
"""

import uuid
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from ..core.hashing import get_password_hash
from ..models import user as models
from ..schemas import user as schemas


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Retrieves a single user record from the database by their email address.

    This function is commonly used during user authentication to find a user
    based on the provided email.

    Args:
        db (Session): The SQLAlchemy database session.
        email (str): The email address of the user to retrieve.

    Returns:
        Optional[models.User]: The `User` ORM object if a user with the given email is found;
                               otherwise, `None`.

    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_users_by_ids(db: Session, user_ids: list[uuid.UUID]) -> list[models.User]:
    """Retrieves multiple users by their list of UUIDs.
    This is more efficient than fetching users one by one.
    """
    return db.query(models.User).filter(models.User.id.in_(user_ids)).all()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    """Retrieves a paginated list of multiple user records from the database.

    This function is typically used by administrative interfaces to view all
    registered users, with support for pagination.

    Args:
        db (Session): The SQLAlchemy database session.
        skip (int): The number of records to skip (offset) for pagination. Defaults to 0.
        limit (int): The maximum number of records to return (limit) for pagination. Defaults to 100.

    Returns:
        list[models.User]: A list of `User` ORM objects.

    """
    return db.query(models.User).offset(skip).limit(limit).all()


def get(db: Session, id: uuid.UUID) -> Optional[models.User]:
    """Retrieves a single user record from the database by their unique ID.

    Args:
        db (Session): The SQLAlchemy database session.
        id (Any): The unique identifier (ID) of the user to retrieve. Can be an integer or UUID.

    Returns:
        Optional[models.User]: The `User` ORM object if a user with the given ID is found;
                               otherwise, `None`.

    """
    return db.query(models.User).filter(models.User.id == id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Creates a new user record in the database.

    This function takes a `UserCreate` Pydantic schema object, hashes the provided
    password for security, and then creates a new `User` ORM object. The new user
    is added to the database session, committed, and refreshed to reflect its
    database state.

    Args:
        db (Session): The SQLAlchemy database session.
        user (schemas.UserCreate): A Pydantic schema object containing the data
                                   for the new user (email, password, role).

    Returns:
        models.User: The newly created `User` ORM object, as it exists in the database.

    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email, hashed_password=hashed_password, role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update(
    db: Session,
    db_obj: models.User,  # The existing user object to be updated.
    obj_in: Union[schemas.UserUpdate, Dict[str, Any]],  # The new data for the update.
) -> models.User:
    """Updates an existing user record in the database.

    This function takes an existing `User` ORM object and new data (either a Pydantic
    `UserUpdate` schema or a dictionary) and applies the updates. It handles password
    hashing if a new password is provided and only updates fields that are present
    in the input data.

    Args:
        db (Session): The SQLAlchemy database session.
        db_obj (models.User): The existing `User` ORM object to update.
        obj_in (Union[schemas.UserUpdate, Dict[str, Any]]): The new data to apply.
                                                              If a Pydantic model, only
                                                              set fields are used.

    Returns:
        models.User: The updated `User` ORM object.

    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    for field in update_data:
        if hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_push_token(
    db: Session, user_id: Any, push_token: str
) -> Optional[models.User]:
    """Updates a user's push notification token in the database.

    This function finds a user by their ID and updates their `push_token` field.
    This is crucial for enabling push notifications to specific user devices.

    Args:
        db (Session): The SQLAlchemy database session.
        user_id (Any): The unique ID of the user whose push token is to be updated.
        push_token (str): The new push notification token string.

    Returns:
        Optional[models.User]: The updated `User` ORM object if the user is found and updated;
                               otherwise, `None`.

    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.push_token = push_token
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def delete(db: Session, id: uuid.UUID) -> Optional[models.User]:
    """Deletes a single user record from the database by their unique ID.

    Args:
        db (Session): The SQLAlchemy database session.
        id (Any): The unique identifier (ID) of the user to delete.

    Returns:
        Optional[models.User]: The deleted `User` ORM object if found and deleted;
                               otherwise, `None`.

    """
    obj = db.query(models.User).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
