"""encryption_context.py

This file defines the Pydantic schema for the homomorphic encryption context.
It is used to serialize and deserialize the public part of the encryption context
that is sent to federated learning clients.

Purpose:
- To provide a structured format for transmitting the encryption context.
- To ensure type validation for the encryption context data.

Key Components:
- `EncryptionContext`: A Pydantic model representing the encryption context.
"""

import base64

from pydantic import BaseModel, field_validator


class EncryptionContext(BaseModel):
    """Pydantic schema for the homomorphic encryption context.

    Attributes:
        context (str): The serialized public encryption context as a Base64 string.

    """

    context: str

    @field_validator("context", mode="before")
    def encode_context_to_base64(cls, v):
        if isinstance(v, bytes):
            return base64.b64encode(v).decode("utf-8")
        return v

    @field_validator("context", mode="after")
    def decode_context_from_base64(cls, v):
        if isinstance(v, str):
            try:
                # Attempt to decode from base64, then re-encode to bytes to ensure it's valid
                decoded_bytes = base64.b64decode(v)
                return base64.b64encode(decoded_bytes).decode("utf-8")
            except Exception:
                raise ValueError("Context must be a valid Base64 encoded string")
        return v
