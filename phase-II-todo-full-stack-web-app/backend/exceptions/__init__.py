"""
Comprehensive custom exceptions for the Todo application backend.
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class TodoAPIException(HTTPException):
    """Base exception for all Todo API exceptions."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


# Authentication Exceptions
class AuthenticationError(TodoAPIException):
    """Base exception for authentication errors."""

    def __init__(self, detail: str, error_code: str = "AUTH_ERROR"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"}
        )


class InvalidCredentialsError(AuthenticationError):
    """Exception raised when credentials are invalid."""

    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail=detail, error_code="INVALID_CREDENTIALS")


class InvalidTokenError(AuthenticationError):
    """Exception raised when token is invalid or expired."""

    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(detail=detail, error_code="INVALID_TOKEN")


class TokenExpiredError(AuthenticationError):
    """Exception raised when token has expired."""

    def __init__(self, detail: str = "Token has expired"):
        super().__init__(detail=detail, error_code="TOKEN_EXPIRED")


# Authorization Exceptions
class AuthorizationError(TodoAPIException):
    """Base exception for authorization errors."""

    def __init__(self, detail: str, error_code: str = "AUTHORIZATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code
        )


class InsufficientPermissionsError(AuthorizationError):
    """Exception raised when user lacks required permissions."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail=detail, error_code="INSUFFICIENT_PERMISSIONS")


class ResourceAccessDeniedError(AuthorizationError):
    """Exception raised when access to resource is denied."""

    def __init__(self, detail: str = "Access to this resource is denied"):
        super().__init__(detail=detail, error_code="RESOURCE_ACCESS_DENIED")


# User Exceptions
class UserError(TodoAPIException):
    """Base exception for user-related errors."""

    def __init__(self, detail: str, status_code: int, error_code: str):
        super().__init__(status_code=status_code, detail=detail, error_code=error_code)


class UserNotFoundError(UserError):
    """Exception raised when user is not found."""

    def __init__(self, detail: str = "User not found"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="USER_NOT_FOUND"
        )


class EmailAlreadyExistsError(UserError):
    """Exception raised when email is already registered."""

    def __init__(self, detail: str = "Email already registered"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="EMAIL_ALREADY_EXISTS"
        )


class EmailNotVerifiedError(UserError):
    """Exception raised when email is not verified."""

    def __init__(self, detail: str = "Email verification required"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="EMAIL_NOT_VERIFIED"
        )


class AccountLockedError(UserError):
    """Exception raised when account is locked."""

    def __init__(self, detail: str = "Account is locked"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="ACCOUNT_LOCKED"
        )


class AccountInactiveError(UserError):
    """Exception raised when account is inactive."""

    def __init__(self, detail: str = "Account is inactive"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="ACCOUNT_INACTIVE"
        )


# Task Exceptions
class TaskError(TodoAPIException):
    """Base exception for task-related errors."""

    def __init__(self, detail: str, status_code: int, error_code: str):
        super().__init__(status_code=status_code, detail=detail, error_code=error_code)


class TaskNotFoundError(TaskError):
    """Exception raised when task is not found."""

    def __init__(self, detail: str = "Task not found"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="TASK_NOT_FOUND"
        )


class TaskAccessDeniedError(TaskError):
    """Exception raised when user doesn't have access to task."""

    def __init__(self, detail: str = "You don't have access to this task"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="TASK_ACCESS_DENIED"
        )


class TaskValidationError(TaskError):
    """Exception raised when task data is invalid."""

    def __init__(self, detail: str = "Invalid task data"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="TASK_VALIDATION_ERROR"
        )


# Validation Exceptions
class ValidationError(TodoAPIException):
    """Base exception for validation errors."""

    def __init__(self, detail: str, error_code: str = "VALIDATION_ERROR", errors: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code
        )
        self.errors = errors


class WeakPasswordError(ValidationError):
    """Exception raised when password doesn't meet strength requirements."""

    def __init__(self, detail: str = "Password does not meet strength requirements"):
        super().__init__(detail=detail, error_code="WEAK_PASSWORD")


class InvalidInputError(ValidationError):
    """Exception raised when input data is invalid."""

    def __init__(self, detail: str = "Invalid input data", errors: Optional[Dict[str, Any]] = None):
        super().__init__(detail=detail, error_code="INVALID_INPUT", errors=errors)


# Rate Limiting Exceptions
class RateLimitError(TodoAPIException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
            headers={"Retry-After": str(retry_after)}
        )


# Database Exceptions
class DatabaseError(TodoAPIException):
    """Base exception for database errors."""

    def __init__(self, detail: str = "Database error occurred", error_code: str = "DATABASE_ERROR"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code
        )


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection fails."""

    def __init__(self, detail: str = "Database connection failed"):
        super().__init__(detail=detail, error_code="DATABASE_CONNECTION_ERROR")


class DatabaseQueryError(DatabaseError):
    """Exception raised when database query fails."""

    def __init__(self, detail: str = "Database query failed"):
        super().__init__(detail=detail, error_code="DATABASE_QUERY_ERROR")


# External Service Exceptions
class ExternalServiceError(TodoAPIException):
    """Base exception for external service errors."""

    def __init__(self, detail: str = "External service error", error_code: str = "EXTERNAL_SERVICE_ERROR"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code=error_code
        )


class EmailServiceError(ExternalServiceError):
    """Exception raised when email service fails."""

    def __init__(self, detail: str = "Email service unavailable"):
        super().__init__(detail=detail, error_code="EMAIL_SERVICE_ERROR")


# Request Exceptions
class RequestError(TodoAPIException):
    """Base exception for request errors."""

    def __init__(self, detail: str, status_code: int, error_code: str):
        super().__init__(status_code=status_code, detail=detail, error_code=error_code)


class RequestTooLargeError(RequestError):
    """Exception raised when request body is too large."""

    def __init__(self, detail: str = "Request body too large"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            error_code="REQUEST_TOO_LARGE"
        )


class InvalidRequestFormatError(RequestError):
    """Exception raised when request format is invalid."""

    def __init__(self, detail: str = "Invalid request format"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_REQUEST_FORMAT"
        )


class MissingRequiredFieldError(RequestError):
    """Exception raised when required field is missing."""

    def __init__(self, field_name: str):
        super().__init__(
            detail=f"Required field '{field_name}' is missing",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="MISSING_REQUIRED_FIELD"
        )


# Resource Exceptions
class ResourceError(TodoAPIException):
    """Base exception for resource errors."""

    def __init__(self, detail: str, status_code: int, error_code: str):
        super().__init__(status_code=status_code, detail=detail, error_code=error_code)


class ResourceNotFoundError(ResourceError):
    """Exception raised when resource is not found."""

    def __init__(self, resource_type: str = "Resource"):
        super().__init__(
            detail=f"{resource_type} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND"
        )


class ResourceConflictError(ResourceError):
    """Exception raised when resource conflict occurs."""

    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            error_code="RESOURCE_CONFLICT"
        )


class ResourceAlreadyExistsError(ResourceError):
    """Exception raised when resource already exists."""

    def __init__(self, resource_type: str = "Resource"):
        super().__init__(
            detail=f"{resource_type} already exists",
            status_code=status.HTTP_409_CONFLICT,
            error_code="RESOURCE_ALREADY_EXISTS"
        )
