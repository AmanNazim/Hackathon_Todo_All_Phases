"""
Privacy enforcement middleware for user profile visibility.

This module provides middleware to enforce privacy settings on profile access,
ensuring users can only view profiles based on visibility rules.
"""

from typing import Optional
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from models import User, UserPreferences


async def enforce_privacy_middleware(
    request: Request,
    target_user_id: str,
    current_user: Optional[User],
    db: Session
) -> None:
    """
    Enforce privacy rules for profile access.

    Args:
        request: FastAPI request object
        target_user_id: ID of the user whose profile is being accessed
        current_user: Currently authenticated user (None if not authenticated)
        db: Database session

    Raises:
        HTTPException: 403 if access is denied based on privacy settings
    """
    # Users can always access their own profile
    if current_user and str(current_user.id) == target_user_id:
        return

    # Get target user's preferences
    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == target_user_id
    ).first()

    if not preferences:
        # Default to public if no preferences set
        return

    privacy_settings = preferences.privacy or {}
    profile_visibility = privacy_settings.get("profile_visibility", "public")

    # Enforce visibility rules
    if profile_visibility == "private":
        # Only the user can view their own profile
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This profile is private"
        )
    elif profile_visibility == "contacts":
        # Only contacts can view (for now, treat as private since we don't have contacts feature)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This profile is only visible to contacts"
            )
        # TODO: Check if current_user is in target_user's contacts
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This profile is only visible to contacts"
        )
    # "public" - allow access


def filter_profile_fields(
    user: User,
    preferences: Optional[UserPreferences],
    current_user: Optional[User]
) -> dict:
    """
    Filter profile fields based on privacy settings.

    Args:
        user: User whose profile is being accessed
        preferences: User's privacy preferences
        current_user: Currently authenticated user (None if not authenticated)

    Returns:
        Dictionary with filtered profile data
    """
    # Users can see all their own fields
    if current_user and str(current_user.id) == str(user.id):
        return {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "avatar_thumbnail_url": user.avatar_thumbnail_url,
            "created_at": user.created_at,
            "last_login_at": user.last_login_at
        }

    # Get privacy settings
    privacy_settings = {}
    if preferences:
        privacy_settings = preferences.privacy or {}

    show_email = privacy_settings.get("show_email", False)
    show_activity = privacy_settings.get("show_activity", False)

    # Build filtered profile
    profile = {
        "id": str(user.id),
        "display_name": user.display_name,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "avatar_thumbnail_url": user.avatar_thumbnail_url
    }

    # Add email if allowed
    if show_email:
        profile["email"] = user.email

    # Add activity if allowed
    if show_activity:
        profile["created_at"] = user.created_at
        profile["last_login_at"] = user.last_login_at

    return profile


def check_email_visibility(
    target_user_id: str,
    current_user: Optional[User],
    db: Session
) -> bool:
    """
    Check if email should be visible to current user.

    Args:
        target_user_id: ID of the user whose email visibility is being checked
        current_user: Currently authenticated user
        db: Database session

    Returns:
        True if email should be visible, False otherwise
    """
    # Users can always see their own email
    if current_user and str(current_user.id) == target_user_id:
        return True

    # Get target user's preferences
    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == target_user_id
    ).first()

    if not preferences:
        return False

    privacy_settings = preferences.privacy or {}
    return privacy_settings.get("show_email", False)


def check_activity_visibility(
    target_user_id: str,
    current_user: Optional[User],
    db: Session
) -> bool:
    """
    Check if activity should be visible to current user.

    Args:
        target_user_id: ID of the user whose activity visibility is being checked
        current_user: Currently authenticated user
        db: Database session

    Returns:
        True if activity should be visible, False otherwise
    """
    # Users can always see their own activity
    if current_user and str(current_user.id) == target_user_id:
        return True

    # Get target user's preferences
    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == target_user_id
    ).first()

    if not preferences:
        return False

    privacy_settings = preferences.privacy or {}
    return privacy_settings.get("show_activity", False)
