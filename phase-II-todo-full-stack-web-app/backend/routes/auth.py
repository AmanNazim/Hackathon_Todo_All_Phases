"""
User profile routes for the Todo application API.

Note: Authentication (register, login, logout, forgot-password, reset-password)
is handled by Better Auth on the frontend. This file only contains endpoints
for user profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models import User, UserRead
from auth import get_current_user, TokenData

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get the current authenticated user's profile.

    Args:
        current_user: The currently authenticated user from JWT token
        session: Database session

    Returns:
        User profile data

    Raises:
        HTTPException: If user is not found
    """
    user = session.exec(select(User).where(User.id == current_user.user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
