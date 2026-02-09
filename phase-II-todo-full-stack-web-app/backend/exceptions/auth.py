"""
Authentication-related custom exceptions.
"""

from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    """Base exception for authentication errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=status_code, detail=detail)


class InvalidCredentialsError(AuthenticationError):
    """Exception raised when credentials are invalid."""

    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class EmailAlreadyExistsError(HTTPException):
    """Exception raised when email is already registered."""

    def __init__(self, detail: str = "Email already registered"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UserNotFoundError(HTTPException):
    """Exception raised when user is not found."""

    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InvalidTokenError(AuthenticationError):
    """Exception raised when token is invalid."""

    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class EmailNotVerifiedError(HTTPException):
    """Exception raised when email is not verified."""

    def __init__(self, detail: str = "Email verification required"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class AccountLockedError(HTTPException):
    """Exception raised when account is locked."""

    def __init__(self, detail: str = "Account is locked due to too many failed login attempts"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class WeakPasswordError(HTTPException):
    """Exception raised when password doesn't meet strength requirements."""

    def __init__(self, detail: str = "Password does not meet strength requirements"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
