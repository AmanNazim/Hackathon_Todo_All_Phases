"""
Authentication middleware for the Todo application.
"""

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import verify_token, TokenData
from typing import Optional

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Get the current authenticated user from the token.

    Args:
        credentials: The HTTP authorization credentials containing the token

    Returns:
        The authenticated user's token data

    Raises:
        HTTPException: If the token is invalid or user is not found
    """
    token = credentials.credentials
    token_data = verify_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


async def require_auth(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Require authentication for a route.

    Args:
        current_user: The current authenticated user

    Returns:
        The authenticated user's token data

    Raises:
        HTTPException: If user is not authenticated
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def require_verified_email(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Require email verification for sensitive operations.

    Args:
        current_user: The current authenticated user

    Returns:
        The authenticated user's token data

    Raises:
        HTTPException: If email is not verified
    """
    # Note: This will be fully implemented when email_verified field is added to User model
    # For now, we just ensure user is authenticated
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required for this operation",
        )
    return current_user
