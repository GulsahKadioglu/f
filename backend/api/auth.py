# -*- coding: utf-8 -*-
"""auth.py

This file defines the API endpoints related to user authentication and management.
It handles operations such as user login, registration, profile retrieval and update,
and registration of push notification tokens. All endpoints are built using FastAPI
and interact with the database via SQLAlchemy ORM.

Purpose:
- To provide secure authentication mechanisms (OAuth2 compatible).
- To manage user accounts, including creation, retrieval, and updates.
- To handle push notification token registration for mobile clients.
- To enforce role-based access control (e.g., admin-only endpoints).

Key Components:
- `APIRouter`: Organizes authentication-related endpoints.
- `OAuth2PasswordRequestForm`: For handling standard OAuth2 password flow.
- `crud.user`: Database interaction layer for user-related operations.
- `schemas`: Pydantic models for request and response data validation.
- `backend.core.security`: Utility functions for password hashing, token creation,
  and dependency injection for current user retrieval.
"""

from uuid import UUID

from backend import crud, schemas
from backend.core.exceptions import (
    DuplicateEntryException,
    ResourceNotFoundException,
)
from backend.core.hashing import verify_password
from backend.core.security import (
    create_access_token,
    get_current_admin_user,
    get_current_user,
)
from backend.db.session import get_db
from backend.schemas.token import Token
from backend.schemas.user import User, UserCreate, UserPushToken, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/login/access-token",
    response_model=Token,
    # dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login, get an access token for future requests.

    This endpoint handles user authentication. It expects a username (email)
    and password, verifies them against the database, and if successful,
    returns an OAuth2 access token.

    Args:
        db (Session): The database session dependency. Provided by `get_db`.
        form_data (OAuth2PasswordRequestForm): The user's credentials, automatically
                                               parsed from the request body by FastAPI.

    Returns:
        schemas.Token: A Pydantic model containing the generated access token
                       and token type (e.g., "bearer").

    Raises:
        HTTPException: If authentication fails (e.g., incorrect email or password),
                       an HTTP 401 Unauthorized error is returned.

    """
    user = crud.user.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/users/",
    response_model=schemas.User,
    # dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
def create_user_open(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create new user without needing authentication.

    This endpoint allows new users to register themselves without prior authentication.
    It checks for existing users with the same email to prevent duplicates.

    Args:
        user_in (schemas.UserCreate): The Pydantic model containing the new user's details
                                      (e.g., email, password, role).
        db (Session): The database session dependency.

    Returns:
        schemas.User: The newly created user object, excluding sensitive information like the hashed password.

    Raises:
        DuplicateEntryException: If a user with the provided email already exists.

    """
    user = crud.user.get_user_by_email(db, email=user_in.email)
    if user:
        raise DuplicateEntryException(detail="This email is already registered.")
    user = crud.user.create_user(db, user=user_in)
    return user


@router.post(
    "/admin/create-user-by-admin",
    response_model=schemas.User,
    dependencies=[Depends(get_current_admin_user)],
)
def create_user_by_admin(
    user_in: UserCreate,  # Pydantic model for user creation request body.
    db: Session = Depends(get_db),  # Dependency to inject a database session.
):
    """Creates a new user by an administrative user.

    This endpoint is restricted to admin users. It takes user details,
    checks if the email is already registered, and if not, creates a new user
    in the database.

    Args:
        user_in (UserCreate): The user details for the new user.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        DuplicateEntryException: If a user with the same email already exists.

    Returns:
        schemas.User: The newly created user object, including its ID and hashed password.

    """
    user = crud.user.get_user_by_email(db, email=user_in.email)
    if user:
        raise DuplicateEntryException(detail="This email is already registered.")
    user = crud.user.create_user(db, user=user_in)
    return user


@router.get("/users/me", response_model=schemas.User)
def read_users_me(
    current_user: User = Depends(
        get_current_user
    ),  # Dependency to get the authenticated user.
):
    """Get current user's profile.

    This endpoint allows an authenticated user to retrieve their own profile information.
    The `get_current_user` dependency automatically extracts the user from the token
    and injects it into the function.

    Args:
        current_user (schemas.User): The Pydantic model representing the currently
                                     authenticated user, injected by FastAPI's dependency system.

    Returns:
        schemas.User: The profile details of the current user.

    """
    return current_user


@router.put("/users/me", response_model=schemas.User)
def update_user_me(
    user_in: UserUpdate,  # Pydantic model for the user's updated details.
    db: Session = Depends(get_db),  # Database session dependency.
    current_user: User = Depends(get_current_user),  # Authenticated user dependency.
):
    """Update current user's profile.

    This endpoint allows an authenticated user to update their own profile information.
    It takes the updated details, retrieves the user from the database, and applies
    the changes.

    Args:
        user_in (UserUpdate): The Pydantic model containing the fields to be updated.
                              Only provided fields will be changed.
        db (Session): The database session dependency.
        current_user (User): The currently authenticated user, whose profile will be updated.

    Returns:
        schemas.User: The updated user object.

    Raises:
        HTTPException: If the user is not found (though this should ideally not happen
                       if `get_current_user` works correctly), an HTTP 404 Not Found error is returned.

    """
    user = crud.user.get(db, id=current_user.id)
    if not user:
        raise ResourceNotFoundException(detail="User not found.")
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.post("/users/register-push-token", status_code=status.HTTP_200_OK)
def register_push_token(
    token_data: UserPushToken,  # Pydantic model containing the push token string.
    db: Session = Depends(get_db),  # Database session dependency.
    current_user: User = Depends(get_current_user),  # Authenticated user dependency.
):
    """Register or update user's push notification token.

    This endpoint allows a mobile client to register or update its push notification
    token (e.g., FCM token) for the authenticated user. This token is used to send
    notifications to the specific device.

    Args:
        token_data (UserPushToken): The Pydantic model containing the push token string.
        db (Session): The database session dependency.
        current_user (User): The currently authenticated user, whose token will be registered.

    Returns:
        dict: A message indicating the success of the registration and the registered token.

    """
    crud.user.update_push_token(
        db, user_id=current_user.id, push_token=token_data.token
    )
    return {"message": "Push token successfully registered.", "token": token_data.token}


@router.get(
    "/users/",
    response_model=list[
        schemas.User
    ],  # Specifies that the response will be a list of User schemas.
    dependencies=[
        Depends(get_current_admin_user)
    ],  # Ensures only admin users can access this endpoint.
)
def read_users(
    db: Session = Depends(get_db),  # Database session dependency.
    skip: int = 0,  # Query parameter for pagination: number of records to skip.
    limit: int = 100,  # Query parameter for pagination: maximum number of records to return.
):
    """Retrieve a list of users.

    This endpoint is accessible only by authenticated admin users. It allows for
    retrieving a paginated list of all registered users in the system.

    Args:
        db (Session): The database session dependency.
        skip (int): The number of records to skip (for pagination). Defaults to 0.
        limit (int): The maximum number of records to return (for pagination). Defaults to 100.

    Returns:
        list[schemas.User]: A list of user objects, each conforming to the `schemas.User` Pydantic model.

    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.put(
    "/users/{user_id}",
    response_model=schemas.User,
    dependencies=[Depends(get_current_admin_user)],
)
def update_user_by_id(
    user_id: UUID,  # Path parameter for the user's ID.
    user_in: UserUpdate,  # Pydantic model for the user's updated details.
    db: Session = Depends(get_db),  # Database session dependency.
):
    """Update a user's profile by ID (Admin only).

    This endpoint allows an authenticated admin user to update any user's profile information.
    It takes the user's ID and the updated details, retrieves the user from the database,
    and applies the changes.

    Args:
        user_id (UUID): The unique identifier of the user to update.
        user_in (UserUpdate): The Pydantic model containing the fields to be updated.
                              Only provided fields will be changed.
        db (Session): The database session dependency.

    Returns:
        schemas.User: The updated user object.

    Raises:
        ResourceNotFoundException: If the user with the given ID is not found.

    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise ResourceNotFoundException(detail="User not found.")
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin_user)],
)
def delete_user_by_id(
    user_id: UUID,  # Path parameter for the user's ID.
    db: Session = Depends(get_db),  # Database session dependency.
):
    """Delete a user by ID (Admin only).

    This endpoint allows an authenticated admin user to delete any user from the system.

    Args:
        user_id (UUID): The unique identifier of the user to delete.
        db (Session): The database session dependency.

    Returns:
        None: Returns a 204 No Content status on successful deletion.

    Raises:
        ResourceNotFoundException: If the user with the given ID is not found.

    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise ResourceNotFoundException(detail="User not found.")
    crud.user.delete(db, id=user_id)
    return