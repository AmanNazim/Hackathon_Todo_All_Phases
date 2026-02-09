"""
Rate limiting middleware for authentication endpoints.
"""

from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

# In-memory storage for rate limiting (use Redis in production)
# Structure: {ip_address: {endpoint: [(timestamp, success), ...]}}
rate_limit_storage: Dict[str, Dict[str, list]] = {}

# Rate limit configuration
MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
CLEANUP_INTERVAL_MINUTES = 60


def get_client_ip(request: Request) -> str:
    """
    Get the client IP address from the request.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address
    """
    # Check for X-Forwarded-For header (when behind a proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # Check for X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct client IP
    return request.client.host if request.client else "unknown"


def cleanup_old_entries():
    """
    Clean up old rate limit entries to prevent memory bloat.
    Should be called periodically.
    """
    cutoff_time = datetime.utcnow() - timedelta(minutes=CLEANUP_INTERVAL_MINUTES)

    for ip in list(rate_limit_storage.keys()):
        for endpoint in list(rate_limit_storage[ip].keys()):
            # Remove old attempts
            rate_limit_storage[ip][endpoint] = [
                (timestamp, success)
                for timestamp, success in rate_limit_storage[ip][endpoint]
                if timestamp > cutoff_time
            ]

            # Remove empty endpoint entries
            if not rate_limit_storage[ip][endpoint]:
                del rate_limit_storage[ip][endpoint]

        # Remove empty IP entries
        if not rate_limit_storage[ip]:
            del rate_limit_storage[ip]


def check_rate_limit(ip_address: str, endpoint: str) -> Tuple[bool, int]:
    """
    Check if the IP address has exceeded the rate limit for the endpoint.

    Args:
        ip_address: Client IP address
        endpoint: Endpoint being accessed

    Returns:
        Tuple of (is_allowed, remaining_attempts)
    """
    cleanup_old_entries()

    if ip_address not in rate_limit_storage:
        rate_limit_storage[ip_address] = {}

    if endpoint not in rate_limit_storage[ip_address]:
        rate_limit_storage[ip_address][endpoint] = []

    # Get attempts within the lockout window
    cutoff_time = datetime.utcnow() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)
    recent_attempts = [
        (timestamp, success)
        for timestamp, success in rate_limit_storage[ip_address][endpoint]
        if timestamp > cutoff_time
    ]

    # Count failed attempts
    failed_attempts = sum(1 for _, success in recent_attempts if not success)

    # Check if locked out
    if failed_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
        remaining_attempts = 0
        is_allowed = False
    else:
        remaining_attempts = MAX_FAILED_LOGIN_ATTEMPTS - failed_attempts
        is_allowed = True

    return is_allowed, remaining_attempts


def record_attempt(ip_address: str, endpoint: str, success: bool):
    """
    Record an authentication attempt.

    Args:
        ip_address: Client IP address
        endpoint: Endpoint being accessed
        success: Whether the attempt was successful
    """
    if ip_address not in rate_limit_storage:
        rate_limit_storage[ip_address] = {}

    if endpoint not in rate_limit_storage[ip_address]:
        rate_limit_storage[ip_address][endpoint] = []

    rate_limit_storage[ip_address][endpoint].append((datetime.utcnow(), success))

    logger.info(
        f"Recorded {'successful' if success else 'failed'} attempt for {ip_address} on {endpoint}"
    )


def reset_attempts(ip_address: str, endpoint: str):
    """
    Reset rate limit attempts for an IP address and endpoint.

    Args:
        ip_address: Client IP address
        endpoint: Endpoint being accessed
    """
    if ip_address in rate_limit_storage and endpoint in rate_limit_storage[ip_address]:
        rate_limit_storage[ip_address][endpoint] = []
        logger.info(f"Reset attempts for {ip_address} on {endpoint}")


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to enforce rate limiting on authentication endpoints.

    Args:
        request: FastAPI request object
        call_next: Next middleware or route handler

    Returns:
        Response from the next handler

    Raises:
        HTTPException: If rate limit is exceeded
    """
    # Only apply rate limiting to authentication endpoints
    auth_endpoints = ["/api/v1/auth/login", "/api/v1/auth/register"]

    if request.url.path in auth_endpoints:
        ip_address = get_client_ip(request)
        endpoint = request.url.path

        # Check rate limit
        is_allowed, remaining_attempts = check_rate_limit(ip_address, endpoint)

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {ip_address} on {endpoint}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed attempts. Please try again in {LOCKOUT_DURATION_MINUTES} minutes.",
                headers={"Retry-After": str(LOCKOUT_DURATION_MINUTES * 60)}
            )

        # Add remaining attempts to response headers
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining_attempts)

        return response

    # For non-auth endpoints, just pass through
    return await call_next(request)
