"""
Privacy service for enforcing privacy settings and visibility controls.
"""

from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from models import User, UserPreferences
from fastapi import HTTPException, status


def get_user_privacy_settings(db: Session, user_id: UUID) -> dict:
    """
    Get user's privacy settings.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Privacy settings dictionary
    """
    statement = select(UserPreferences).where(UserPreferences.user_id == user_id)
    preferences = db.exec(statement).first()

    if not preferences or not preferences.privacy:
        # Return default privacy settings
        return {
            "profile_visibility": "private",
            "show_email": False,
            "show_activity": False,
            "show_tasks": False
        }

    return preferences.privacy


def check_profile_visibility(
    db: Session,
    profile_owner_id: UUID,
    viewer_id: Optional[UUID] = None
) -> bool:
    """
    Check if a user can view another user's profile based on privacy settings.

    Args:
        db: Database session
        profile_owner_id: ID of the profile owner
        viewer_id: ID of the user trying to view the profile (None for anonymous)

    Returns:
        True if profile is visible, False otherwise
    """
    # Users can always view their own profile
    if viewer_id and profile_owner_id == viewer_id:
        return True

    # Get privacy settings
    privacy_settings = get_user_privacy_settings(db, profile_owner_id)
    visibility = privacy_settings.get("profile_visibility", "private")

    if visibility == "public":
        return True
    elif visibility == "private":
        return False
    elif visibility == "contacts":
        # For now, treat contacts as private
        # In a full implementation, this would check a contacts/friends table
        return False

    return False


def check_email_visibility(
    db: Session,
    profile_owner_id: UUID,
    viewer_id: Optional[UUID] = None
) -> bool:
    """
    Check if a user's email should be visible to another user.

    Args:
        db: Database session
        profile_owner_id: ID of the profile owner
        viewer_id: ID of the user trying to view the email

    Returns:
        True if email is visible, False otherwise
    """
    # Users can always see their own email
    if viewer_id and profile_owner_id == viewer_id:
        return True

    # Get privacy settings
    privacy_settings = get_user_privacy_settings(db, profile_owner_id)
    show_email = privacy_settings.get("show_email", False)

    # Check if profile is visible first
    if not check_profile_visibility(db, profile_owner_id, viewer_id):
        return False

    return show_email


def check_activity_visibility(
    db: Session,
    profile_owner_id: UUID,
    viewer_id: Optional[UUID] = None
) -> bool:
    """
    Check if a user's activity should be visible to another user.

    Args:
        db: Database session
        profile_owner_id: ID of the profile owner
        viewer_id: ID of the user trying to view the activity

    Returns:
        True if activity is visible, False otherwise
    """
    # Users can always see their own activity
    if viewer_id and profile_owner_id == viewer_id:
        return True

    # Get privacy settings
    privacy_settings = get_user_privacy_settings(db, profile_owner_id)
    show_activity = privacy_settings.get("show_activity", False)

    # Check if profile is visible first
    if not check_profile_visibility(db, profile_owner_id, viewer_id):
        return False

    return show_activity


def check_tasks_visibility(
    db: Session,
    profile_owner_id: UUID,
    viewer_id: Optional[UUID] = None
) -> bool:
    """
    Check if a user's tasks should be visible to another user.

    Args:
        db: Database session
        profile_owner_id: ID of the profile owner
        viewer_id: ID of the user trying to view the tasks

    Returns:
        True if tasks are visible, False otherwise
    """
    # Users can always see their own tasks
    if viewer_id and profile_owner_id == viewer_id:
        return True

    # Get privacy settings
    privacy_settings = get_user_privacy_settings(db, profile_owner_id)
    show_tasks = privacy_settings.get("show_tasks", False)

    # Check if profile is visible first
    if not check_profile_visibility(db, profile_owner_id, viewer_id):
        return False

    return show_tasks


def enforce_visibility_rules(
    db: Session,
    profile_owner_id: UUID,
    viewer_id: Optional[UUID] = None,
    resource_type: str = "profile"
) -> None:
    """
    Enforce visibility rules and raise exception if access is denied.

    Args:
        db: Database session
        profile_owner_id: ID of the profile owner
        viewer_id: ID of the user trying to view
        resource_type: Type of resource (profile, email, activity, tasks)

    Raises:
        HTTPException: If access is denied
    """
    visibility_checks = {
        "profile": check_profile_visibility,
        "email": check_email_visibility,
        "activity": check_activity_visibility,
        "tasks": check_tasks_visibility
    }

    check_function = visibility_checks.get(resource_type, check_profile_visibility)

    if not check_function(db, profile_owner_id, viewer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have permission to view this user's {resource_type}"
        )


def filter_profile_data(
    db: Session,
    user: User,
    viewer_id: Optional[UUID] = None
) -> dict:
    """
    Filter profile data based on privacy settings.

    Args:
        db: Database session
        user: User object
        viewer_id: ID of the user viewing the profile

    Returns:
        Filtered profile data dictionary
    """
    # Start with basic profile data
    profile_data = {
        "id": user.id,
        "display_name": user.display_name,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "avatar_thumbnail_url": user.avatar_thumbnail_url
    }

    # Check if email should be visible
    if check_email_visibility(db, user.id, viewer_id):
        profile_data["email"] = user.email
        profile_data["email_verified"] = user.email_verified

    # Check if activity should be visible
    if check_activity_visibility(db, user.id, viewer_id):
        profile_data["last_login_at"] = user.last_login_at
        profile_data["created_at"] = user.created_at

    return profile_data
