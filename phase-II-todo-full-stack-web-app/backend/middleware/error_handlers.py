"""
Comprehensive error handling middleware and exception handlers.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging
import traceback
from datetime import datetime
from typing import Union, Dict, Any

logger = logging.getLogger(__name__)


def format_error_response(
    error_type: str,
    message: str,
    status_code: int,
    error_code: str = None,
    details: Dict[str, Any] = None,
    path: str = None
) -> Dict[str, Any]:
    """
    Format error response in a consistent structure.

    Args:
        error_type: Type of error
        message: Error message
        status_code: HTTP status code
        error_code: Application-specific error code
        details: Additional error details
        path: Request path where error occurred

    Returns:
        Formatted error response dictionary
    """
    response = {
        "error": {
            "type": error_type,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

    if error_code:
        response["error"]["code"] = error_code

    if details:
        response["error"]["details"] = details

    if path:
        response["error"]["path"] = path

    return response


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request
        exc: Validation error exception

    Returns:
        JSON response with validation error details
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=format_error_response(
            error_type="ValidationError",
            message="Request validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details={"errors": errors},
            path=str(request.url.path)
        )
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.

    Args:
        request: FastAPI request
        exc: HTTP exception

    Returns:
        JSON response with error details
    """
    # Check if exception has error_code attribute (custom exceptions)
    error_code = getattr(exc, "error_code", None)

    logger.warning(
        f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            error_type="HTTPException",
            message=exc.detail,
            status_code=exc.status_code,
            error_code=error_code,
            path=str(request.url.path)
        ),
        headers=exc.headers
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle database errors.

    Args:
        request: FastAPI request
        exc: SQLAlchemy exception

    Returns:
        JSON response with error details
    """
    logger.error(f"Database error on {request.url.path}: {str(exc)}")
    logger.error(traceback.format_exc())

    # Check for specific database errors
    if isinstance(exc, IntegrityError):
        error_message = "Database integrity constraint violated"
        error_code = "DATABASE_INTEGRITY_ERROR"
        status_code = status.HTTP_409_CONFLICT
    else:
        error_message = "A database error occurred"
        error_code = "DATABASE_ERROR"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(
        status_code=status_code,
        content=format_error_response(
            error_type="DatabaseError",
            message=error_message,
            status_code=status_code,
            error_code=error_code,
            path=str(request.url.path)
        )
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}")
    logger.error(traceback.format_exc())

    # Don't expose internal error details in production
    error_message = "An unexpected error occurred"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_error_response(
            error_type="InternalServerError",
            message=error_message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            path=str(request.url.path)
        )
    )


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle 404 Not Found errors.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=format_error_response(
            error_type="NotFound",
            message=f"The requested resource was not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            path=str(request.url.path)
        )
    )


async def method_not_allowed_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle 405 Method Not Allowed errors.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        content=format_error_response(
            error_type="MethodNotAllowed",
            message=f"Method {request.method} not allowed for this endpoint",
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            error_code="METHOD_NOT_ALLOWED",
            path=str(request.url.path)
        )
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from sqlalchemy.exc import SQLAlchemyError

    # Register handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Exception handlers registered successfully")
