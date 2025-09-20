# -*- coding: utf-8 -*-
"""user.py

This file defines the SQLAlchemy ORM model for `User`.
It represents a user record in the database, including their unique identifier,
email, hashed password, activity status, assigned role, and push notification token.

Purpose:
- To define the database schema for storing user account information.
- To provide an ORM (Object-Relational Mapping) representation of users
  for easy interaction with the database.
- To support different user roles (e.g., admin, doctor) for access control.
- To store push notification tokens for mobile application integration.

Key Components:
- `UserRole` enum: Defines the possible roles a user can have.
- `User` class: Defines the database table structure and column types.
- `Base`: The declarative base class from SQLAlchemy, which all ORM models inherit from.
- `UUID` (from `sqlalchemy.dialects.postgresql`): Used for generating UUID primary keys.
"""

import enum
import uuid

from sqlalchemy import Boolean, Column, Enum, String
from backend.db.types import GUID

from backend.db.base_class import Base


class UserRole(str, enum.Enum):
    """An enumeration defining the possible roles that a user can have within the application.

    This enum ensures that the `role` field in the `User` model can only take on
    predefined, valid values, which is crucial for implementing role-based access control (RBAC).

    Values:
        ADMIN (str): Represents an administrative user with elevated privileges,
                     typically able to manage other users, system settings, etc.
        DOCTOR (str): Represents a regular user, typically a medical professional,
                      who can manage medical cases and reports.
    """

    ADMIN = "admin"
    DOCTOR = "doctor"

    def get_permissions(self) -> list["Permission"]:
        if self == UserRole.ADMIN:
            return [
                Permission.FL_INITIATE_ROUND,
                Permission.REPORT_VIEW_ALL,
                Permission.USER_MANAGE,
                Permission.VIEW_FL_METRICS,
                Permission.VIEW_MODEL_VERSIONS,
                Permission.CASE_MANAGE,
                Permission.REPORT_MANAGE,
                Permission.HEATMAP_GENERATE,
                Permission.CREATE_REPORT,
                Permission.CREATE_FL_METRIC,
                Permission.READ_FL_METRIC,
                Permission.DELETE_FL_METRIC,
                Permission.UPDATE_FL_METRIC,
            ]
        elif self == UserRole.DOCTOR:
            return [
                Permission.REPORT_VIEW_OWN,
                Permission.CASE_MANAGE,
                Permission.CASE_VIEW_OWN,
                Permission.HEATMAP_GENERATE,
                Permission.VIEW_FL_METRICS,
                Permission.VIEW_MODEL_VERSIONS,
            ]
        return []


class Permission(str, enum.Enum):
    """An enumeration defining granular permissions for actions within the application.

    This enum provides a set of fine-grained permissions that can be assigned to
    user roles. This allows for a more flexible and secure authorization system
    than relying solely on broad roles.
    """

    FL_INITIATE_ROUND = "fl:initiate_round"
    REPORT_VIEW_ALL = "report:view_all"
    REPORT_VIEW_OWN = "report:view_own"
    REPORT_MANAGE = "report:manage"
    USER_MANAGE = "user:manage"
    CASE_MANAGE = "case:manage"
    CASE_VIEW_OWN = "case:view_own"
    HEATMAP_GENERATE = "heatmap:generate"
    VIEW_FL_METRICS = "fl:view_metrics"
    VIEW_MODEL_VERSIONS = "model:view_versions"
    CREATE_REPORT = "report:create"
    CREATE_FL_METRIC = "fl:create_metric"
    READ_FL_METRIC = "fl:read_metric"
    DELETE_FL_METRIC = "fl:delete_metric"
    UPDATE_FL_METRIC = "fl:update_metric"


class User(Base):
    """SQLAlchemy ORM model representing a user record in the database.

    This table stores essential user information, including authentication credentials
    (hashed password), contact details (email), and authorization attributes (role, active status).

    Attributes:
        __tablename__ (str): The name of the database table for this model.
        id (uuid.UUID): The primary key of the `users` table. It's a UUID,
                        automatically generated upon creation. `as_uuid=True` ensures
                        it's handled as a Python `uuid.UUID` object.
        email (str): The user's email address. It must be unique and is indexed for
                     efficient lookups. `nullable=False` ensures it's always present.
        hashed_password (str): The securely hashed version of the user's password.
                               `nullable=False` ensures this field is always present.
        is_active (bool): A boolean flag indicating whether the user account is active.
                           Defaults to `True`. Inactive users cannot log in.
        role (UserRole): The user's role within the application, using the `UserRole` enum.
                         Defaults to `UserRole.DOCTOR`. This determines access privileges.
        push_token (str): An optional string to store a push notification token for the user's device.
                          `nullable=True` as not all users may have a token registered.
        mfa_secret (str): The secret key for multi-factor authentication.
        mfa_enabled (bool): A boolean flag indicating whether MFA is enabled for the user.

    """

    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    role = Column(Enum(UserRole), default=UserRole.DOCTOR)
    push_token = Column(String, nullable=True)
    mfa_secret = Column(String, nullable=True)
    mfa_enabled = Column(Boolean(), default=False)