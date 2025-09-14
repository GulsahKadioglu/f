# -*- coding: utf-8 -*-
"""mfa.py

This file defines the API endpoints for Multi-Factor Authentication (MFA).
"""

from .deps import get_current_active_user, get_db
from ..models.user import User
from ..schemas.mfa import MFACode, MFASetupResponse
from ..services import mfa_service
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/setup", response_model=MFASetupResponse)
def setup_mfa(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Sets up MFA for the current user.

    This endpoint generates a new MFA secret and returns it to the user,
    along with a QR code for easy setup in an authenticator app.
    """
    try:
        secret = mfa_service.generate_mfa_secret(db, user=current_user)
        provisioning_uri, qr_code_base64 = mfa_service.get_mfa_qr_code_uri(
            secret, current_user.email, "FastAPIMFA"
        )
    except mfa_service.MFAAlreadyEnabledException as e:
        raise HTTPException(status_code=400, detail=str(e))

    return MFASetupResponse(
        email=current_user.email,
        id=current_user.id,
        is_active=current_user.is_active,
        role=current_user.role,
        mfa_enabled=current_user.mfa_enabled,
        mfa_secret=current_user.mfa_secret,
        secret=secret,
        qr_code_base64=qr_code_base64,
        provisioning_uri=provisioning_uri,
    )


@router.post("/verify-setup", response_model=User)
def verify_mfa_setup(
    mfa_code: MFACode,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Verifies the MFA setup and enables MFA for the user."""
    try:
        updated_user = mfa_service.enable_mfa(
            db, user=current_user, code=mfa_code.otp_code
        )
        return updated_user
    except (
        mfa_service.MFAAlreadyEnabledException,
        mfa_service.MFANotEnabledException,
        mfa_service.MFAVerificationFailedException,
    ) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/disable", response_model=User)
def disable_mfa(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Disables MFA for the current user."""
    try:
        updated_user = mfa_service.disable_mfa(db, user=current_user)
        return updated_user
    except mfa_service.MFANotEnabledException as e:
        raise HTTPException(status_code=400, detail=str(e))