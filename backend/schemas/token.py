"""token.py

This file defines Pydantic schemas for JSON Web Tokens (JWTs).
These schemas are used for data validation, serialization, and deserialization
of token-related data, ensuring consistency when handling authentication tokens
within the API.

Purpose:
- To define the structure of JWT access tokens for API responses.
- To define the expected structure of JWT payloads.
- To provide a structured way to represent extracted token data for authentication purposes.

Key Components:
- `Token`: Schema for the full access token response (token string and type).
- `TokenPayload`: Schema for the data contained within the JWT itself (e.g., subject).
- `TokenData`: Schema for the parsed and validated data extracted from a token,
  used internally for authentication logic.
- `BaseModel`: Pydantic's base class for creating data models.
"""

from pydantic import BaseModel


class Token(BaseModel):
    """Pydantic schema representing a JWT access token for API responses.

    This schema is used to define the structure of the response when a user
    successfully authenticates and receives an access token.

    Attributes:
        access_token (str): The actual JWT string that clients will use for authentication.
        token_type (str): The type of the token, typically "bearer" for OAuth2 Bearer tokens.

    """

    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Pydantic schema representing the payload structure of a JWT token.

    This schema defines the expected claims (data fields) within the JWT.
    The `sub` (subject) claim is typically used to store the user's identifier.

    Attributes:
        sub (str | None): The subject of the token, usually the user's email or ID.
                          It can be `None` if the token is malformed or for specific token types.

    """

    sub: str | None = None


class TokenData(BaseModel):
    """Pydantic schema representing the data extracted from a JWT token for authentication purposes.

    This schema is used internally by authentication dependencies to hold the
    validated user identifier (email) after decoding the JWT.

    Attributes:
        email (str | None): The email address of the user, extracted from the token's payload.
                            It can be `None` if the email claim is missing or invalid.

    """

    email: str | None = None
