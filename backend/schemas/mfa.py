# -*- coding: utf-8 -*-
"""mfa.py

This file defines the Pydantic schemas for Multi-Factor Authentication (MFA).
"""

from pydantic import BaseModel

from user import User


class MFASetupResponse(User):
    """Schema for the MFA setup response.

    This schema extends the `User` schema with MFA-specific fields.
    """

    secret: str
    qr_code_base64: str
    provisioning_uri: str


class MFACode(BaseModel):
    """Schema for the MFA code.

    This schema is used to validate the MFA code provided by the user.
    """

    otp_code: str
