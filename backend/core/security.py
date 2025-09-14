# -*- coding: utf-8 -*-
"""
security.py

This file contains core security-related functions for the application.
It handles password hashing and verification, JSON Web Token (JWT) creation
and decoding, and dependency injection for authenticating and authorizing
users in FastAPI endpoints.

Purpose:
- To provide a centralized location for all authentication and authorization logic.
- To securely manage user credentials and access tokens.
- To define reusable FastAPI dependencies for protecting endpoints based on
  user status (e.g., logged in, active, admin) and permissions.

Key Components:
- `pwd_context`: A Passlib context for hashing and verifying passwords using bcrypt.
- `oauth2_scheme`: A FastAPI security scheme for handling OAuth2 password flow.
- `verify_password`, `get_password_hash`: Functions for password management.
- `create_access_token`: Function to generate a JWT access token.
- `get_current_user`, `get_current_active_user`, `get_current_admin_user`:
  FastAPI dependency functions to retrieve the current user from a token and
  enforce basic authorization.
- `has_permission`: A dependency factory for creating permission-based access checks.
"""

from datetime import datetime, timedelta

from .config import settings
from ..crud import user as user_crud
from ..db.session import get_db
from ..models.user import Permission, User, UserRole
from ..schemas.token import TokenData
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Creates a JWT access token.

    The token contains the provided data and an expiration timestamp.

    Args:
        data (dict): The data to encode in the token (e.g., {"sub": user_email}).
        expires_delta (timedelta, optional): The duration for which the token
                                             is valid. Defaults to the value from
                                             settings.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    FastAPI dependency to get the current user from an OAuth2 access token.

    This function decodes the JWT token from the request's Authorization header,
    extracts the user's email, and retrieves the corresponding user object
    from the database.

    Args:
        db (Session): The database session dependency.
        token (str): The OAuth2 access token, injected by FastAPI.

    Returns:
        User: The SQLAlchemy User object corresponding to the token.

    Raises:
        HTTPException: An HTTP 401 Unauthorized error if the token is invalid,
                       expired, or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = user_crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    FastAPI dependency to get the current, active user.

    This builds on `get_current_user` and adds a check to ensure the user
    is marked as active in the database.

    Args:
        current_user (User): The user object, injected by `get_current_user`.

    Returns:
        User: The active user object.

    Raises:
        HTTPException: An HTTP 400 Bad Request error if the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    FastAPI dependency to ensure the current user is an administrator.

    This builds on `get_current_active_user` and adds a check to ensure the
    user has the ADMIN role.

    Args:
        current_user (User): The active user object, injected by
                               `get_current_active_user`.

    Returns:
        User: The admin user object.

    Raises:
        HTTPException: An HTTP 403 Forbidden error if the user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


def has_permission(permission: Permission):
    """
    Factory function that creates a FastAPI dependency to check for a specific permission.

    This allows for creating dynamic permission checks for endpoints, for example:
    `Depends(has_permission(Permission.CREATE_REPORT))`

    Args:
        permission (Permission): The permission to check for.

    Returns:
        function: A FastAPI dependency function that will perform the permission check.
    """

    def permission_checker(current_user: User = Depends(get_current_active_user)):
        """
        Inner function that performs the actual permission check.

        It retrieves the current active user and verifies if their role includes
        the required permission.

        Args:
            current_user (User): The active user, injected by dependency.

        Returns:
            User: The user object if they have the required permission.

        Raises:
            HTTPException: An HTTP 403 Forbidden error if the user lacks the
                           required permission.
        """
        if permission not in current_user.role.get_permissions():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have permission: {permission.value}",
            )
        return current_user

    return permission_checker
