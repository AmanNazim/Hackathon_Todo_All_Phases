"""
User preferences routes for the Todo application API.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models import (
    UserPreferences, PreferencesRead, PreferencesUpdate,
    NotificationSettings, PrivacySettings
)
from auth import get_current_user, TokenData

router = APIRouter(prefix="/api/v1/users/{user_id}", tags=["preferences"])


@router.get("/preferences", response_model=PreferencesRead)
async def get_user_preferences(
    user_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve user preferences.

    Args:
        user_id: The UUID of the user
        current_user: The currently authenticated user
        session: Database session

    Returns:
        User preferences data

    Raises:
        HTTPException: If user is not authorized or preferences not found
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these preferences"
        )

    # Query for preferences
    statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
    preferences = session.exec(statement).first()

    if not preferences:
        # Create default preferences if they don't exist
        preferences = UserPreferences(
            user_id=user_id,
            theme="system",
            language="en",
            notifications={
                "email_notifications": True,
                "push_notifications": False,
                "task_reminders": True,
                "task_assignments": True,
                "task_completions": False,
                "weekly_summary": True
            },
            privacy={
                "profile_visibility": "private",
                "show_email": False,
                "show_activity": False,
                "show_tasks": False
            }
        )
        session.add(preferences)
        session.commit()
        session.refresh(preferences)

    return preferences


@router.put("/preferences", response_model=PreferencesRead)
async def update_user_preferences(
    user_id: UUID,
    preferences_update: PreferencesUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update user preferences.

    Args:
        user_id: The UUID of the user
        preferences_update: Preferences update data
        current_user: The currently authenticated user
        session: Database session

    Returns:
        Updated user preferences data

    Raises:
        HTTPException: If user is not authorized or preferences not found
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update these preferences"
        )

    # Query for preferences
    statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
    preferences = session.exec(statement).first()

    if not preferences:
        # Create preferences if they don't exist
        preferences = UserPreferences(user_id=user_id)
        session.add(preferences)

    # Update preferences fields
    update_dict = preferences_update.dict(exclude_unset=True)

    for field, value in update_dict.items():
        if field == "notifications" and value is not None:
            # Merge notification settings
            current_notifications = preferences.notifications or {}
            current_notifications.update(value.dict())
            preferences.notifications = current_notifications
        elif field == "privacy" and value is not None:
            # Merge privacy settings
            current_privacy = preferences.privacy or {}
            current_privacy.update(value.dict())
            preferences.privacy = current_privacy
        else:
            setattr(preferences, field, value)

    preferences.updated_at = datetime.utcnow()
    session.add(preferences)
    session.commit()
    session.refresh(preferences)

    return preferences


@router.get("/preferences/theme")
async def get_theme_preference(
    user_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get user's theme preference.

    Args:
        user_id: The UUID of the user
        current_user: The currently authenticated user
        session: Database session

    Returns:
        Theme preference

    Raises:
        HTTPException: If user is not authorized
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these preferences"
        )

    # Query for preferences
    statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
    preferences = session.exec(statement).first()

    theme = preferences.theme if preferences else "system"

    return {"theme": theme}


@router.put("/preferences/theme")
async def update_theme_preference(
    user_id: UUID,
    theme: str,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update user's theme preference.

    Args:
        user_id: The UUID of the user
        theme: Theme value (light, dark, system)
        current_user: The currently authenticated user
        session: Database session

    Returns:
        Updated theme preference

    Raises:
        HTTPException: If user is not authorized or invalid theme
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update these preferences"
        )

    # Validate theme
    if theme not in ["light", "dark", "system"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid theme. Must be 'light', 'dark', or 'system'"
        )

    # Query for preferences
    statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
    preferences = session.exec(statement).first()

    if not preferences:
        preferences = UserPreferences(user_id=user_id, theme=theme)
        session.add(preferences)
    else:
        preferences.theme = theme
        preferences.updated_at = datetime.utcnow()
        session.add(preferences)

    session.commit()
    session.refresh(preferences)

    return {"theme": preferences.theme}
