"""
Authentication utilities for the Todo application.
Integrates with Better Auth JWT tokens from the frontend.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize JWT settings for Better Auth integration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required")

ALGORITHM = "HS256"

security = HTTPBearer()

class TokenData(BaseModel):
    """Model for token data."""
    user_id: Optional[str] = None
    email: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """
    Hash a plain password.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify and decode a Better Auth JWT token.

    Args:
        token: The JWT token to verify

    Returns:
        TokenData if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])

        # Better Auth tokens may use different field names
        # Try multiple possible field names for user ID
        user_id = payload.get("sub") or payload.get("userId") or payload.get("id") or payload.get("user_id")
        email = payload.get("email")

        if user_id is None:
            return None

        token_data = TokenData(user_id=str(user_id), email=email)
        return token_data
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
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