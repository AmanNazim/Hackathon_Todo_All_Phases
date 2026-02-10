"""
JWT Authentication Middleware for Better Auth Integration

This middleware verifies JWT tokens issued by Better Auth on the frontend
and extracts the user information for use in API endpoints.
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import os

# Get the shared secret from environment variable
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "")

if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required")

security = HTTPBearer()


def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token from Better Auth and extract user information.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded token payload containing user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode and verify the JWT token
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(request: Request) -> dict:
    """
    Extract and verify the current user from the JWT token in the request.

    Args:
        request: FastAPI request object

    Returns:
        dict: User information from the JWT token

    Raises:
        HTTPException: If token is missing or invalid
    """
    # Get the Authorization header
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract the token (format: "Bearer <token>")
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify the token and extract user info
    user_data = verify_jwt_token(token)

    return user_data


def get_user_id_from_token(user_data: dict) -> str:
    """
    Extract user ID from the decoded JWT token.

    Args:
        user_data: Decoded JWT token payload

    Returns:
        str: User ID

    Raises:
        HTTPException: If user ID is not found in token
    """
    user_id = user_data.get("sub") or user_data.get("userId") or user_data.get("id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )

    return str(user_id)
