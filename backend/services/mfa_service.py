# -*- coding: utf-8 -*-
"""mfa_service.py

This file provides the business logic for Multi-Factor Authentication (MFA).
"""

import io
from base64 import b64encode

import pyotp
import qrcode
from  import crud, schemas
from backend.models.user import User
from sqlalchemy.orm import Session


class MFAAlreadyEnabledException(Exception):
    """Raised when MFA is already enabled for a user."""

    pass


class MFANotEnabledException(Exception):
    """Raised when MFA is not enabled for a user."""

    pass


class MFAActivationFailedException(Exception):
    """Raised when MFA activation fails."""

    pass


class MFAVerificationFailedException(Exception):
    """Raised when MFA verification fails."""

    pass


def generate_mfa_secret(db: Session, user: User) -> str:
    """Generates a new MFA secret for a user.

    If the user already has a secret, it will be overwritten.
    """
    if user.mfa_enabled:
        raise MFAAlreadyEnabledException("MFA is already enabled for this user.")

    secret = pyotp.random_base32()
    user_update = schemas.UserUpdate(mfa_secret=secret, email=user.email)
    crud.user.update(db, db_obj=user, obj_in=user_update)
    return secret


def get_mfa_qr_code_uri(secret: str, email: str, issuer_name: str) -> tuple[str, str]:
    """Generates a QR code URI for the MFA secret.

    Returns the provisioning URI and the QR code image in base64 format.
    """
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=email, issuer_name=issuer_name
    )

    img = qrcode.make(provisioning_uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_code_base64 = b64encode(buf.getvalue()).decode("utf-8")

    return provisioning_uri, qr_code_base64


def verify_mfa_code(secret: str, code: str) -> bool:
    """Verifies an MFA code.

    Returns True if the code is valid, False otherwise.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


def enable_mfa(db: Session, user: User, code: str) -> User:
    """Enables MFA for a user.

    Verifies the MFA code and enables MFA for the user.
    """
    if user.mfa_enabled:
        raise MFAAlreadyEnabledException("MFA is already enabled for this user.")

    if not user.mfa_secret:
        raise MFANotEnabledException("MFA not set up. Please run /setup first.")

    if not verify_mfa_code(user.mfa_secret, code):
        raise MFAVerificationFailedException("Invalid OTP code.")

    user_update = schemas.UserUpdate(mfa_enabled=True, email=user.email)
    updated_user = crud.user.update(db, db_obj=user, obj_in=user_update)
    return updated_user


def disable_mfa(db: Session, user: User) -> User:
    """Disables MFA for a user."""
    if not user.mfa_enabled:
        raise MFANotEnabledException("MFA is not enabled for this user.")

    user_update = schemas.UserUpdate(
        mfa_enabled=False, mfa_secret=None, email=user.email
    )
    updated_user = crud.user.update(db, db_obj=user, obj_in=user_update)
    return updated_user
