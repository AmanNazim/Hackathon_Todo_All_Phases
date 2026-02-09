"""Authentication dependencies for API endpoints"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verify authentication token and extract user_id.

    This is a placeholder implementation. In production, this should:
    1. Verify the JWT token with Better Auth
    2. Check token expiration
    3. Extract user_id from token payload
    4. Validate user exists

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        user_id: Authenticated user identifier

    Raises:
        HTTPException: 401 if token invalid or missing
    """
    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: Integrate with Better Auth for token verification
    # For now, extract user_id from token (placeholder)
    # In production, decode JWT and verify signature

    # Placeholder: Accept any token and return test user
    # Replace with actual Better Auth integration
    user_id = "test_user"

    return user_id


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> str:
    """
    Optional authentication - returns user_id if authenticated, None otherwise.

    Args:
        credentials: Optional bearer token

    Returns:
        user_id or None
    """
    if credentials:
        return await get_current_user(credentials)
    return None
