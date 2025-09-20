# -*- coding: utf-8 -*-
"""
hashing.py

This file contains password hashing and verification functions.
It is separated from security.py to avoid circular dependencies.
"""

from passlib.context import CryptContext
from passlib.hash import bcrypt

# Force bcrypt to use the 'bcrypt' backend, preventing fallback to 'os_crypt'
# and avoiding the DeprecationWarning for the 'crypt' module.
bcrypt.set_backend("bcrypt")

pwd_context = CryptContext(schemes=[bcrypt], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password.

    Args:
        plain_password (str): The plain-text password to verify.
        hashed_password (str): The hashed password from the database.

    Returns:
        bool: True if the password is correct, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password using the configured hashing algorithm (bcrypt).

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The resulting hashed password.
    """
    return pwd_context.hash(password)
