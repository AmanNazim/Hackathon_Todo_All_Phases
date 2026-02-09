"""
Request size limit middleware to prevent large payload attacks.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Default size limits (in bytes)
DEFAULT_MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_JSON_SIZE = 1 * 1024 * 1024  # 1 MB for JSON
MAX_FORM_SIZE = 5 * 1024 * 1024  # 5 MB for forms
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB for files


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce request size limits.

    Prevents denial-of-service attacks via large payloads.
    """

    def __init__(
        self,
        app,
        max_request_size: int = DEFAULT_MAX_REQUEST_SIZE,
        max_json_size: int = MAX_JSON_SIZE,
        max_form_size: int = MAX_FORM_SIZE
    ):
        """
        Initialize the middleware.

        Args:
            app: FastAPI application
            max_request_size: Maximum request size in bytes
            max_json_size: Maximum JSON payload size in bytes
            max_form_size: Maximum form data size in bytes
        """
        super().__init__(app)
        self.max_request_size = max_request_size
        self.max_json_size = max_json_size
        self.max_form_size = max_form_size

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and enforce size limits.

        Args:
            request: Incoming request
            call_next: Next middleware or route handler

        Returns:
            Response from the next handler

        Raises:
            HTTPException: If request size exceeds limits
        """
        # Get content length from headers
        content_length = request.headers.get("content-length")

        if content_length:
            content_length = int(content_length)

            # Check overall request size
            if content_length > self.max_request_size:
                logger.warning(
                    f"Request size {content_length} exceeds maximum {self.max_request_size}"
                )
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request body too large. Maximum size is {self.max_request_size / (1024 * 1024):.1f} MB"
                )

            # Check content-type specific limits
            content_type = request.headers.get("content-type", "")

            if "application/json" in content_type and content_length > self.max_json_size:
                logger.warning(
                    f"JSON payload size {content_length} exceeds maximum {self.max_json_size}"
                )
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"JSON payload too large. Maximum size is {self.max_json_size / (1024 * 1024):.1f} MB"
                )

            if "multipart/form-data" in content_type and content_length > self.max_form_size:
                logger.warning(
                    f"Form data size {content_length} exceeds maximum {self.max_form_size}"
                )
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Form data too large. Maximum size is {self.max_form_size / (1024 * 1024):.1f} MB"
                )

        # Process the request
        response = await call_next(request)
        return response


async def check_file_size(file_size: int, max_size: int = MAX_FILE_SIZE) -> None:
    """
    Check if uploaded file size is within limits.

    Args:
        file_size: Size of the uploaded file in bytes
        max_size: Maximum allowed file size in bytes

    Raises:
        HTTPException: If file size exceeds limit
    """
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {max_size / (1024 * 1024):.1f} MB"
        )
