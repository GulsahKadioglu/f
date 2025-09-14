# -*- coding: utf-8 -*-
"""types.py

This file defines custom SQLAlchemy data types to ensure database-agnostic
handling of specific data formats, such as Globally Unique Identifiers (GUIDs).

Purpose:
- To provide a consistent data type for GUIDs (UUIDs) that works across
  different database backends (e.g., PostgreSQL and SQLite).
- To abstract the database-specific implementation details of data types
  from the application's models.

Key Components:
- `GUID`: A custom SQLAlchemy `TypeDecorator` for handling UUIDs.
"""

import uuid
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class GUID(TypeDecorator):
    """Platform-independent GUID type for SQLAlchemy.

    This custom type decorator ensures that UUIDs are handled correctly across
    different database backends. It uses the native UUID type when connected to
    PostgreSQL for optimal performance and storage. For other databases (like SQLite),
    it falls back to using a 32-character CHAR field, storing the UUID as a hex string.

    Attributes:
        impl (TypeEngine): The underlying SQLAlchemy type to use when a specific
                         dialect is not handled. Defaults to CHAR.
        cache_ok (bool): Indicates that this type is safe to be cached by the
                         SQLAlchemy engine.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Loads the appropriate implementation based on the database dialect.

        This method is called by SQLAlchemy when the type is used. It checks the
        name of the database dialect and returns the best-suited type descriptor.

        Args:
            dialect: The SQLAlchemy dialect object for the current database connection.

        Returns:
            TypeEngine: The dialect-specific type implementation (e.g., PG_UUID or CHAR).
        """
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        """Processes the Python value before sending it to the database.

        This method converts the Python `uuid.UUID` object into a format that can
        be stored in the database. For PostgreSQL, it's a string representation.
        For other backends, it's the 32-character hex string.

        Args:
            value: The value being sent to the database column (e.g., a `uuid.UUID` object).
            dialect: The SQLAlchemy dialect object.

        Returns:
            str or None: The processed value ready for database storage.
        """
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if isinstance(value, int):
                return str(value)
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value).hex
            else:
                # hexstring
                return value.hex

    def process_result_value(self, value, dialect):
        """Processes the value received from the database back into a Python object.

        This method converts the string representation from the database back into
        a Python `uuid.UUID` object, ensuring the application always works with
        the correct data type.

        Args:
            value: The raw value received from the database.
            dialect: The SQLAlchemy dialect object.

        Returns:
            uuid.UUID or None: The processed value as a `uuid.UUID` object.
        """
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value
