# -*- coding: utf-8 -*-
"""encryption_service.py

This file provides services for both symmetric and homomorphic encryption.
It is used to encrypt and decrypt sensitive medical images for secure storage
and to manage the cryptographic context for federated learning with secure
aggregation.

Purpose:
- To provide symmetric encryption (Fernet) for securing medical image files at rest.
- To manage the lifecycle of the TenSEAL context required for homomorphic
  encryption in the federated learning process.
- To abstract the complexities of cryptography from the rest of the application.

Key Components:
- `_derive_key`: Derives a stable encryption key from the application's secret key.
- `encrypt_file_content`, `decrypt_file_content`: Functions for symmetric
  encryption and decryption of file data.
- `get_context`, `get_public_context`: Functions for creating and serializing
  the TenSEAL context for homomorphic encryption.
"""

import base64

import tenseal as ts
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from backend.core.config import settings


def _derive_key(salt: bytes) -> bytes:
    """Derives a stable 32-byte key from the application's SECRET_KEY and a salt.

    This function uses PBKDF2 (Password-Based Key Derivation Function 2) to
    create a cryptographically strong encryption key. Using a key derivation
    function is a security best practice, as it makes brute-force attacks
    more difficult.

    Args:
        salt (bytes): A random salt value. Using a salt prevents attackers from
                      using precomputed tables (rainbow tables) to crack the key.

    Returns:
        bytes: A URL-safe, base64-encoded 32-byte key suitable for use with Fernet.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # The desired length of the derived key in bytes.
        salt=salt,
        iterations=100000,  # The number of iterations, making it computationally expensive.
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))


# For simplicity in this example, a fixed salt is used. In a production system,
# it is highly recommended to use a unique salt for each piece of data being
# encrypted and to store that salt alongside the encrypted data.
_fixed_salt = b"some_fixed_salt_for_medical_images"
_fernet_key = _derive_key(_fixed_salt)
_fernet = Fernet(_fernet_key)


def encrypt_file_content(data: bytes) -> bytes:
    """Encrypts the given byte data using Fernet symmetric encryption.

    Args:
        data (bytes): The raw byte content to be encrypted.

    Returns:
        bytes: The encrypted data.
    """
    return _fernet.encrypt(data)


def decrypt_file_content(encrypted_data: bytes) -> bytes:
    """Decrypts the given encrypted byte data using Fernet symmetric encryption.

    Args:
        encrypted_data (bytes): The encrypted byte content to be decrypted.

    Returns:
        bytes: The original, decrypted data.
    """
    return _fernet.decrypt(encrypted_data)


def get_context() -> ts.Context:
    """Creates and configures a TenSEAL context for homomorphic encryption.

    This function sets up a TenSEAL context with the CKKS scheme, which is
    suitable for performing arithmetic operations on encrypted floating-point
    numbers. The context is configured with specific parameters for security
    and performance.

    Returns:
        ts.Context: A configured TenSEAL context object.
    """
    # In a real application, this context should be generated once and securely
    # stored and retrieved. For this demonstration, a new one is generated on demand.
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60],
    )
    context.generate_galois_keys()
    context.global_scale = 2**40
    return context


def get_public_context() -> bytes:
    """Serializes the public parts of the TenSEAL context.

    This function creates a TenSEAL context and serializes it. The serialized
    context contains the public key and other parameters needed by clients to
    encrypt their data, but it does not contain the private key, which remains
    on the server.

    Returns:
        bytes: The serialized public TenSEAL context.
    """
    context = get_context()
    # The `private` parameter is False by default, so only public parts are serialized.
    return context.serialize()
