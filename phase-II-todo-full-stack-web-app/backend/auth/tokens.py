"""
Token generation and verification utilities for password reset and email verification.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple


def generate_token(length: int = 32) -> Tuple[str, str]:
    """
    Generate a secure random token and its hash.

    Args:
        length: Length of the token in bytes (default 32)

    Returns:
        Tuple of (plain_token, token_hash)
    """
    # Generate a secure random token
    plain_token = secrets.token_urlsafe(length)

    # Create a hash of the token for storage
    token_hash = hashlib.sha256(plain_token.encode()).hexdigest()

    return plain_token, token_hash


def generate_reset_token() -> Tuple[str, str]:
    """
    Generate a password reset token.

    Returns:
        Tuple of (plain_token, token_hash)
    """
    return generate_token(32)


def generate_verification_token() -> Tuple[str, str]:
    """
    Generate an email verification token.

    Returns:
        Tuple of (plain_token, token_hash)
    """
    return generate_token(32)


def verify_reset_token(plain_token: str, stored_hash: str, expires_at: datetime, used: bool = False) -> bool:
    """
    Verify a password reset token.

    Args:
        plain_token: The plain token provided by the user
        stored_hash: The hashed token stored in the database
        expires_at: The expiration datetime of the token
        used: Whether the token has already been used

    Returns:
        True if token is valid, False otherwise
    """
    # Check if token has been used
    if used:
        return False

    # Check if token has expired
    if datetime.utcnow() > expires_at:
        return False

    # Verify the token hash
    token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
    return token_hash == stored_hash


def verify_email_token(plain_token: str, stored_hash: str, expires_at: datetime) -> bool:
    """
    Verify an email verification token.

    Args:
        plain_token: The plain token provided by the user
        stored_hash: The hashed token stored in the database
        expires_at: The expiration datetime of the token

    Returns:
        True if token is valid, False otherwise
    """
    # Check if token has expired
    if datetime.utcnow() > expires_at:
        return False

    # Verify the token hash
    token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
    return token_hash == stored_hash


def get_reset_token_expiry() -> datetime:
    """
    Get the expiration datetime for a password reset token (1 hour from now).

    Returns:
        Expiration datetime
    """
    return datetime.utcnow() + timedelta(hours=1)


def get_verification_token_expiry() -> datetime:
    """
    Get the expiration datetime for an email verification token (24 hours from now).

    Returns:
        Expiration datetime
    """
    return datetime.utcnow() + timedelta(hours=24)
