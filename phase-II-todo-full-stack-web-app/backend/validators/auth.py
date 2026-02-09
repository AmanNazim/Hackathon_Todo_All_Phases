"""
Authentication validators for input validation.
"""

import re
from typing import Optional
from pydantic import EmailStr, validator
from exceptions.auth import WeakPasswordError


def validate_email(email: str) -> str:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        Validated email address

    Raises:
        ValueError: If email format is invalid
    """
    # Basic email validation (Pydantic EmailStr handles most of this)
    if not email or "@" not in email:
        raise ValueError("Invalid email format")

    # Additional checks
    if len(email) > 255:
        raise ValueError("Email address too long")

    return email.lower()


def validate_password_strength(password: str) -> str:
    """
    Validate password strength requirements.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character

    Args:
        password: Password to validate

    Returns:
        Validated password

    Raises:
        WeakPasswordError: If password doesn't meet requirements
    """
    if len(password) < 8:
        raise WeakPasswordError("Password must be at least 8 characters long")

    if len(password) > 100:
        raise WeakPasswordError("Password must be less than 100 characters")

    if not re.search(r"[A-Z]", password):
        raise WeakPasswordError("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        raise WeakPasswordError("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        raise WeakPasswordError("Password must contain at least one number")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise WeakPasswordError("Password must contain at least one special character")

    return password


def validate_name(name: str, field_name: str = "Name") -> str:
    """
    Validate name fields (first name, last name).

    Args:
        name: Name to validate
        field_name: Name of the field for error messages

    Returns:
        Validated name

    Raises:
        ValueError: If name is invalid
    """
    if not name or not name.strip():
        raise ValueError(f"{field_name} cannot be empty")

    if len(name) < 2:
        raise ValueError(f"{field_name} must be at least 2 characters long")

    if len(name) > 100:
        raise ValueError(f"{field_name} must be less than 100 characters")

    # Allow letters, spaces, hyphens, and apostrophes
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        raise ValueError(f"{field_name} can only contain letters, spaces, hyphens, and apostrophes")

    return name.strip()


def validate_user_registration(email: str, password: str, first_name: str, last_name: str) -> dict:
    """
    Validate all user registration fields.

    Args:
        email: Email address
        password: Password
        first_name: First name
        last_name: Last name

    Returns:
        Dictionary with validated fields

    Raises:
        ValueError or WeakPasswordError: If any field is invalid
    """
    return {
        "email": validate_email(email),
        "password": validate_password_strength(password),
        "first_name": validate_name(first_name, "First name"),
        "last_name": validate_name(last_name, "Last name")
    }
