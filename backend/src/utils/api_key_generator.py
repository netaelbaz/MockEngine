"""API key generator utility for MockEngine."""

import secrets
import hashlib
from typing import Optional


def generate_api_key() -> str:
    """
    Generate a unique API key.

    The key is generated using cryptographically secure random bytes
    and hashed for storage. The returned value is the plain key that
    will be given to the user.

    Returns:
        str: Generated API key (64-character hex string)

    Example:
        >>> generate_api_key()
        'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6'
    """
    # Generate 32 random bytes (256 bits)
    random_bytes = secrets.token_bytes(32)

    # Encode to hex string (64 characters)
    hex_string = random_bytes.hex()

    return hex_string


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.

    Uses SHA-256 to create a one-way hash of the API key.
    This allows verification without storing the original key.

    Args:
        api_key: Plain API key string

    Returns:
        str: Hashed API key

    Example:
        >>> hash_api_key("abc123")
        'a1b2c3d4e5f6...'
    """
    # Use SHA-256 for hashing
    hashed = hashlib.sha256(api_key.encode()).hexdigest()
    return hashed


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verify a plain API key against a hashed key.

    Args:
        plain_key: Plain API key to verify
        hashed_key: Hashed API key to compare against

    Returns:
        bool: True if keys match, False otherwise
    """
    return hash_api_key(plain_key) == hashed_key


def generate_unique_identifier() -> str:
    """
    Generate a unique identifier for API keys or rules.

    Uses URL-safe base64 encoding of random bytes.

    Returns:
        str: Unique identifier string

    Example:
        >>> generate_unique_identifier()
        'AbCdEf123456'
    """
    return secrets.token_urlsafe(16)
