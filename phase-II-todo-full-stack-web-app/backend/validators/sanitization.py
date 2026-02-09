"""
Input sanitization utilities for the Todo application backend.

Provides functions to sanitize user input and prevent injection attacks.
"""

import re
import html
from typing import Optional, Any, Dict, List
import bleach


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize a string input by removing potentially dangerous characters.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        ValueError: If input is invalid
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")

    # Strip leading/trailing whitespace
    sanitized = value.strip()

    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')

    # Escape HTML entities
    sanitized = html.escape(sanitized)

    # Enforce max length if specified
    if max_length and len(sanitized) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length} characters")

    return sanitized


def sanitize_html(value: str, allowed_tags: Optional[List[str]] = None) -> str:
    """
    Sanitize HTML content by removing dangerous tags and attributes.

    Args:
        value: HTML string to sanitize
        allowed_tags: List of allowed HTML tags (default: safe subset)

    Returns:
        Sanitized HTML string
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")

    # Default safe tags for rich text
    if allowed_tags is None:
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a'
        ]

    # Allowed attributes
    allowed_attributes = {
        'a': ['href', 'title'],
        'code': ['class'],
    }

    # Clean the HTML
    cleaned = bleach.clean(
        value,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )

    return cleaned


def sanitize_email(email: str) -> str:
    """
    Sanitize and validate email address.

    Args:
        email: Email address to sanitize

    Returns:
        Sanitized email address

    Raises:
        ValueError: If email format is invalid
    """
    if not isinstance(email, str):
        raise ValueError("Email must be a string")

    # Strip whitespace and convert to lowercase
    sanitized = email.strip().lower()

    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, sanitized):
        raise ValueError("Invalid email format")

    # Check length
    if len(sanitized) > 255:
        raise ValueError("Email address too long")

    return sanitized


def sanitize_url(url: str, allowed_schemes: Optional[List[str]] = None) -> str:
    """
    Sanitize and validate URL.

    Args:
        url: URL to sanitize
        allowed_schemes: List of allowed URL schemes (default: http, https)

    Returns:
        Sanitized URL

    Raises:
        ValueError: If URL is invalid or uses disallowed scheme
    """
    if not isinstance(url, str):
        raise ValueError("URL must be a string")

    # Default allowed schemes
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']

    # Strip whitespace
    sanitized = url.strip()

    # Check for valid URL pattern
    url_pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    if not re.match(url_pattern, sanitized, re.IGNORECASE):
        raise ValueError("Invalid URL format")

    # Check scheme
    scheme = sanitized.split('://')[0].lower()
    if scheme not in allowed_schemes:
        raise ValueError(f"URL scheme '{scheme}' not allowed")

    # Check length
    if len(sanitized) > 2048:
        raise ValueError("URL too long")

    return sanitized


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other attacks.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename

    Raises:
        ValueError: If filename is invalid
    """
    if not isinstance(filename, str):
        raise ValueError("Filename must be a string")

    # Strip whitespace
    sanitized = filename.strip()

    # Remove path separators and null bytes
    sanitized = sanitized.replace('/', '').replace('\\', '').replace('\x00', '')

    # Remove leading dots (hidden files)
    sanitized = sanitized.lstrip('.')

    # Remove dangerous characters
    sanitized = re.sub(r'[<>:"|?*]', '', sanitized)

    # Check if filename is empty after sanitization
    if not sanitized:
        raise ValueError("Invalid filename")

    # Check length
    if len(sanitized) > 255:
        raise ValueError("Filename too long")

    return sanitized


def sanitize_integer(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
    """
    Sanitize and validate integer input.

    Args:
        value: Value to sanitize
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Sanitized integer

    Raises:
        ValueError: If value is not a valid integer or out of range
    """
    try:
        sanitized = int(value)
    except (ValueError, TypeError):
        raise ValueError("Value must be an integer")

    if min_value is not None and sanitized < min_value:
        raise ValueError(f"Value must be at least {min_value}")

    if max_value is not None and sanitized > max_value:
        raise ValueError(f"Value must be at most {max_value}")

    return sanitized


def sanitize_boolean(value: Any) -> bool:
    """
    Sanitize and validate boolean input.

    Args:
        value: Value to sanitize

    Returns:
        Sanitized boolean

    Raises:
        ValueError: If value cannot be converted to boolean
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        lower_value = value.lower().strip()
        if lower_value in ('true', '1', 'yes', 'on'):
            return True
        if lower_value in ('false', '0', 'no', 'off'):
            return False

    if isinstance(value, int):
        return bool(value)

    raise ValueError("Value must be a boolean")


def sanitize_dict(data: Dict[str, Any], allowed_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Sanitize dictionary by removing disallowed keys and sanitizing values.

    Args:
        data: Dictionary to sanitize
        allowed_keys: List of allowed keys (if None, all keys allowed)

    Returns:
        Sanitized dictionary
    """
    if not isinstance(data, dict):
        raise ValueError("Input must be a dictionary")

    sanitized = {}

    for key, value in data.items():
        # Check if key is allowed
        if allowed_keys is not None and key not in allowed_keys:
            continue

        # Sanitize string values
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        else:
            sanitized[key] = value

    return sanitized


def remove_sql_injection_patterns(value: str) -> str:
    """
    Remove common SQL injection patterns from input.

    Note: This is a defense-in-depth measure. Always use parameterized queries.

    Args:
        value: String to check

    Returns:
        Sanitized string

    Raises:
        ValueError: If dangerous SQL patterns are detected
    """
    if not isinstance(value, str):
        return value

    # Common SQL injection patterns
    dangerous_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|#|/\*|\*/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"(;.*--)",
        r"(\bUNION\b.*\bSELECT\b)",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError("Input contains potentially dangerous SQL patterns")

    return value


def remove_xss_patterns(value: str) -> str:
    """
    Remove common XSS attack patterns from input.

    Args:
        value: String to check

    Returns:
        Sanitized string

    Raises:
        ValueError: If dangerous XSS patterns are detected
    """
    if not isinstance(value, str):
        return value

    # Common XSS patterns
    dangerous_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",  # Event handlers like onclick, onload
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError("Input contains potentially dangerous XSS patterns")

    return value


def sanitize_task_input(title: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Sanitize task input data.

    Args:
        title: Task title
        description: Task description

    Returns:
        Dictionary with sanitized task data

    Raises:
        ValueError: If input is invalid
    """
    sanitized = {}

    # Sanitize title
    sanitized['title'] = sanitize_string(title, max_length=255)
    if not sanitized['title']:
        raise ValueError("Task title cannot be empty")

    # Sanitize description if provided
    if description:
        sanitized['description'] = sanitize_string(description, max_length=1000)

    return sanitized


def sanitize_user_input(
    email: str,
    first_name: str,
    last_name: str,
    display_name: Optional[str] = None,
    bio: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sanitize user input data.

    Args:
        email: User email
        first_name: User first name
        last_name: User last name
        display_name: User display name
        bio: User bio

    Returns:
        Dictionary with sanitized user data

    Raises:
        ValueError: If input is invalid
    """
    sanitized = {}

    # Sanitize email
    sanitized['email'] = sanitize_email(email)

    # Sanitize names
    sanitized['first_name'] = sanitize_string(first_name, max_length=100)
    sanitized['last_name'] = sanitize_string(last_name, max_length=100)

    if not sanitized['first_name']:
        raise ValueError("First name cannot be empty")
    if not sanitized['last_name']:
        raise ValueError("Last name cannot be empty")

    # Sanitize optional fields
    if display_name:
        sanitized['display_name'] = sanitize_string(display_name, max_length=100)

    if bio:
        sanitized['bio'] = sanitize_string(bio, max_length=500)

    return sanitized
