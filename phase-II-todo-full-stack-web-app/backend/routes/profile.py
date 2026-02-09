"""
User profile routes for the Todo application API.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models import User, ProfileRead, ProfileUpdate
from auth import get_current_user, TokenData
import html

router = APIRouter(prefix="/api/v1/users/{user_id}", tags=["profile"])


def sanitize_html(text: Optional[str]) -> Optional[str]:
    """Sanitize HTML to prevent XSS attacks."""
    if text is None:
        return None
    return html.escape(text.strip())


@router.get("/profile", response_model=ProfileRead)
async def get_user_profile(
    user_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve user profile information.

    Args:
        user_id: The UUID of the user whose profile to retrieve
        current_user: The currently authenticated user
        session: Database session

    Returns:
        User profile data

    Raises:
        HTTPException: If user is not authorized or profile not found
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )

    # Query for user
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/profile", response_model=ProfileRead)
async def update_user_profile(
    user_id: UUID,
    profile_update: ProfileUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update user profile information.

    Args:
        user_id: The UUID of the user whose profile to update
        profile_update: Profile update data
        current_user: The currently authenticated user
        session: Database session

    Returns:
        Updated user profile data

    Raises:
        HTTPException: If user is not authorized or profile not found
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )

    # Query for user
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update profile fields with sanitization
    update_dict = profile_update.dict(exclude_unset=True)

    for field, value in update_dict.items():
        if field in ['display_name', 'bio'] and value is not None:
            # Sanitize text fields to prevent XSS
            value = sanitize_html(value)
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.get("/profile/completion")
async def get_profile_completion(
    user_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Calculate profile completion percentage.

    Args:
        user_id: The UUID of the user
        current_user: The currently authenticated user
        session: Database session

    Returns:
        Profile completion data

    Raises:
        HTTPException: If user is not authorized or profile not found
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )

    # Query for user
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Calculate completion
    total_fields = 7
    completed_fields = 0

    # Required fields (always present)
    completed_fields += 3  # email, first_name, last_name

    # Optional fields
    if user.display_name:
        completed_fields += 1
    if user.bio:
        completed_fields += 1
    if user.avatar_url:
        completed_fields += 1
    if user.email_verified:
        completed_fields += 1

    completion_percentage = round((completed_fields / total_fields) * 100, 2)

    return {
        "completion_percentage": completion_percentage,
        "completed_fields": completed_fields,
        "total_fields": total_fields,
        "missing_fields": [
            field for field, present in [
                ("display_name", user.display_name),
                ("bio", user.bio),
                ("avatar", user.avatar_url),
                ("email_verified", user.email_verified)
            ] if not present
        ]
    }
