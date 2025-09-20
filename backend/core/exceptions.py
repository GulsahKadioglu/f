# -*- coding: utf-8 -*-
"""exceptions.py

This file defines custom exception classes for the application. These exceptions
are used to handle specific error conditions in a structured way, providing
clear and consistent HTTP responses when raised within API endpoints.

Purpose:
- To create a set of standardized, reusable exceptions for common error
  scenarios (e.g., resource not found, permission denied).
- To map these application-specific exceptions to appropriate HTTP status codes
  and error messages.
- To improve the clarity and consistency of error handling in the API.

Key Components:
- Each class inherits from `fastapi.HTTPException`, allowing them to be
  automatically handled by FastAPI's error handling middleware.
"""

from fastapi import HTTPException, status


class ResourceNotFoundException(HTTPException):
    """Exception raised when a requested resource is not found in the database.

    This exception should be raised when a database query for a specific
    resource (e.g., a user, a medical case) returns no result. It maps to an
    HTTP 404 Not Found response.
    """

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class DuplicateEntryException(HTTPException):
    """Exception raised when attempting to create a resource that already exists.

    This is typically used when a new entry would violate a unique constraint
    in the database (e.g., creating a user with an email that is already
    registered). It maps to an HTTP 409 Conflict response.
    """

    def __init__(self, detail: str = "Duplicate entry"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class BadRequestException(HTTPException):
    """Exception raised for general-purpose bad requests.

    This can be used for validation errors or other client-side mistakes that
    don't fit into a more specific category. It maps to an HTTP 400 Bad Request
    response.
    """

    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class PermissionDeniedException(HTTPException):
    """Exception raised when a user is not authorized to perform an action.

    This should be raised when an authenticated user attempts to access a
    resource or perform an action for which they do not have the necessary
    permissions. It maps to an HTTP 403 Forbidden response.
    """

    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
