"""
Security tests for privacy enforcement.

Tests that privacy settings are properly enforced and unauthorized access is blocked.
"""

import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import User, UserPreferences
from middleware.privacy import (
    enforce_privacy_middleware,
    filter_profile_fields,
    check_email_visibility,
    check_activity_visibility
)
from datetime import datetime
import uuid


@pytest.fixture
def sample_user(db_session: Session) -> User:
    """Create a sample user for testing."""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        display_name="Test User",
        bio="Test bio",
        avatar_url="https://example.com/avatar.jpg",
        avatar_thumbnail_url="https://example.com/avatar_thumb.jpg",
        created_at=datetime.utcnow(),
        last_login_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def other_user(db_session: Session) -> User:
    """Create another user for testing."""
    user = User(
        id=str(uuid.uuid4()),
        email="other@example.com",
        display_name="Other User",
        bio="Other bio",
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def private_preferences(db_session: Session, sample_user: User) -> UserPreferences:
    """Create private preferences for sample user."""
    prefs = UserPreferences(
        user_id=sample_user.id,
        theme="light",
        language="en",
        privacy={
            "profile_visibility": "private",
            "show_email": False,
            "show_activity": False
        }
    )
    db_session.add(prefs)
    db_session.commit()
    return prefs


@pytest.fixture
def public_preferences(db_session: Session, sample_user: User) -> UserPreferences:
    """Create public preferences for sample user."""
    prefs = UserPreferences(
        user_id=sample_user.id,
        theme="light",
        language="en",
        privacy={
            "profile_visibility": "public",
            "show_email": True,
            "show_activity": True
        }
    )
    db_session.add(prefs)
    db_session.commit()
    return prefs


class TestPrivacyEnforcement:
    """Test privacy enforcement middleware."""

    @pytest.mark.asyncio
    async def test_user_can_access_own_profile(
        self, db_session: Session, sample_user: User, private_preferences: UserPreferences
    ):
        """Test that users can always access their own profile."""
        # Should not raise exception
        await enforce_privacy_middleware(
            request=None,
            target_user_id=sample_user.id,
            current_user=sample_user,
            db=db_session
        )

    @pytest.mark.asyncio
    async def test_private_profile_blocks_others(
        self, db_session: Session, sample_user: User, other_user: User, private_preferences: UserPreferences
    ):
        """Test that private profiles block other users."""
        with pytest.raises(HTTPException) as exc_info:
            await enforce_privacy_middleware(
                request=None,
                target_user_id=sample_user.id,
                current_user=other_user,
                db=db_session
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "private" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_private_profile_blocks_anonymous(
        self, db_session: Session, sample_user: User, private_preferences: UserPreferences
    ):
        """Test that private profiles block anonymous users."""
        with pytest.raises(HTTPException) as exc_info:
            await enforce_privacy_middleware(
                request=None,
                target_user_id=sample_user.id,
                current_user=None,
                db=db_session
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_public_profile_allows_access(
        self, db_session: Session, sample_user: User, other_user: User, public_preferences: UserPreferences
    ):
        """Test that public profiles allow access."""
        # Should not raise exception
        await enforce_privacy_middleware(
            request=None,
            target_user_id=sample_user.id,
            current_user=other_user,
            db=db_session
        )

    @pytest.mark.asyncio
    async def test_contacts_only_blocks_non_contacts(
        self, db_session: Session, sample_user: User, other_user: User
    ):
        """Test that contacts-only profiles block non-contacts."""
        prefs = UserPreferences(
            user_id=sample_user.id,
            theme="light",
            language="en",
            privacy={
                "profile_visibility": "contacts",
                "show_email": False,
                "show_activity": False
            }
        )
        db_session.add(prefs)
        db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            await enforce_privacy_middleware(
                request=None,
                target_user_id=sample_user.id,
                current_user=other_user,
                db=db_session
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "contacts" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_nonexistent_user_returns_404(
        self, db_session: Session, other_user: User
    ):
        """Test that accessing nonexistent user returns 404."""
        fake_id = str(uuid.uuid4())
        with pytest.raises(HTTPException) as exc_info:
            await enforce_privacy_middleware(
                request=None,
                target_user_id=fake_id,
                current_user=other_user,
                db=db_session
            )
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestProfileFieldFiltering:
    """Test profile field filtering based on privacy settings."""

    def test_user_sees_all_own_fields(
        self, db_session: Session, sample_user: User, private_preferences: UserPreferences
    ):
        """Test that users see all their own fields."""
        profile = filter_profile_fields(sample_user, private_preferences, sample_user)

        assert profile["id"] == str(sample_user.id)
        assert profile["email"] == sample_user.email
        assert profile["display_name"] == sample_user.display_name
        assert profile["bio"] == sample_user.bio
        assert "created_at" in profile
        assert "last_login_at" in profile

    def test_private_profile_hides_email(
        self, db_session: Session, sample_user: User, other_user: User, private_preferences: UserPreferences
    ):
        """Test that private profiles hide email from others."""
        profile = filter_profile_fields(sample_user, private_preferences, other_user)

        assert "email" not in profile
        assert profile["display_name"] == sample_user.display_name

    def test_private_profile_hides_activity(
        self, db_session: Session, sample_user: User, other_user: User, private_preferences: UserPreferences
    ):
        """Test that private profiles hide activity from others."""
        profile = filter_profile_fields(sample_user, private_preferences, other_user)

        assert "created_at" not in profile
        assert "last_login_at" not in profile

    def test_public_profile_shows_email(
        self, db_session: Session, sample_user: User, other_user: User, public_preferences: UserPreferences
    ):
        """Test that public profiles show email when allowed."""
        profile = filter_profile_fields(sample_user, public_preferences, other_user)

        assert profile["email"] == sample_user.email

    def test_public_profile_shows_activity(
        self, db_session: Session, sample_user: User, other_user: User, public_preferences: UserPreferences
    ):
        """Test that public profiles show activity when allowed."""
        profile = filter_profile_fields(sample_user, public_preferences, other_user)

        assert "created_at" in profile
        assert "last_login_at" in profile


class TestEmailVisibility:
    """Test email visibility checks."""

    def test_user_can_see_own_email(
        self, db_session: Session, sample_user: User, private_preferences: UserPreferences
    ):
        """Test that users can always see their own email."""
        visible = check_email_visibility(sample_user.id, sample_user, db_session)
        assert visible is True

    def test_private_email_hidden_from_others(
        self, db_session: Session, sample_user: User, other_user: User, private_preferences: UserPreferences
    ):
        """Test that private email is hidden from others."""
        visible = check_email_visibility(sample_user.id, other_user, db_session)
        assert visible is False

    def test_public_email_visible_to_others(
        self, db_session: Session, sample_user: User, other_user: User, public_preferences: UserPreferences
    ):
        """Test that public email is visible to others."""
        visible = check_email_visibility(sample_user.id, other_user, db_session)
        assert visible is True


class TestActivityVisibility:
    """Test activity visibility checks."""

    def test_user_can_see_own_activity(
        self, db_session: Session, sample_user: User, private_preferences: UserPreferences
    ):
        """Test that users can always see their own activity."""
        visible = check_activity_visibility(sample_user.id, sample_user, db_session)
        assert visible is True

    def test_private_activity_hidden_from_others(
        self, db_session: Session, sample_user: User, other_user: User, private_preferences: UserPreferences
    ):
        """Test that private activity is hidden from others."""
        visible = check_activity_visibility(sample_user.id, other_user, db_session)
        assert visible is False

    def test_public_activity_visible_to_others(
        self, db_session: Session, sample_user: User, other_user: User, public_preferences: UserPreferences
    ):
        """Test that public activity is visible to others."""
        visible = check_activity_visibility(sample_user.id, other_user, db_session)
        assert visible is True
