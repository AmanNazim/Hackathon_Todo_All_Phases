"""
Custom middleware for the Todo application backend.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import traceback
from datetime import datetime


class LoggingMiddleware:
    """
    Middleware for logging requests and responses.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        start_time = datetime.utcnow()

        # Log incoming request
        logging.info(f"Request: {request.method} {request.url}")

        response_body = b""

        async def send_with_logging(message):
            if message["type"] == "http.response.body":
                nonlocal response_body
                response_body += message.get("body", b"")

            await send(message)

        try:
            await self.app(scope, receive, send_with_logging)
        except Exception as e:
            # Log the exception
            logging.error(f"Unhandled exception: {str(e)}")
            logging.error(traceback.format_exc())
            raise e
        finally:
            # Calculate response time
            process_time = (datetime.utcnow() - start_time).total_seconds()
            logging.info(f"Response time: {process_time:.4f}s")


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Custom handler for general exceptions.
    """
    logging.error(f"Unhandled exception: {str(exc)}")
    logging.error(traceback.format_exc())

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "status_code": 500
        }
    )