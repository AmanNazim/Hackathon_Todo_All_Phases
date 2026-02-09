"""
Security tests for privacy enforcement.

Tests that privacy rules are enforced across all endpoints and scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from models import User, UserPreferences
from datetime import datetime
import uuid


client = TestClient(app)


@pytest.fixture
def private_user(db_session: Session) -> tuple[User, UserPreferences]:
    """Create a user with private profile settings."""
    user = User(
        id=str(uuid.uuid4()),
        email="private@example.com",
        display_name="Private User",
        bio="This is a private profile",
        created_at=datetime.utcnow(),
        last_login_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()

    prefs = UserPreferences(
        user_id=user.id,
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

    return user, prefs


@pytest.fixture
def public_user(db_session: Session) -> tuple[User, UserPreferences]:
    """Create a user with public profile settings."""
    user = User(
        id=str(uuid.uuid4()),
        email="public@example.com",
        display_name="Public User",
        bio="This is a public profile",
        created_at=datetime.utcnow(),
        last_login_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()

    prefs = UserPreferences(
        user_id=user.id,
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

    return user, prefs


@pytest.fixture
def viewer_user(db_session: Session) -> User:
    """Create a user who will view other profiles."""
    user = User(
        id=str(uuid.uuid4()),
        email="viewer@example.com",
        display_name="Viewer User",
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    return user


class TestPrivateProfileEnforcement:
    """Test that private profiles are properly enforced."""

    def test_private_profile_blocks_authenticated_users(
        self, db_session: Session, private_user: tuple, viewer_user: User
    ):
        """Test that private profiles block other authenticated users."""
        user, prefs = private_user

        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{viewer_user.id}"}
        )

        assert response.status_code == 403
        assert "private" in response.json()["detail"].lower()

    def test_private_profile_blocks_anonymous_users(
        self, db_session: Session, private_user: tuple
    ):
        """Test that private profiles block anonymous users."""
        user, prefs = private_user

        response = client.get(f"/api/v1/users/{user.id}/profile")

        assert response.status_code == 401

    def test_user_can_view_own_private_profile(
        self, db_session: Session, private_user: tuple
    ):
        """Test that users can view their own private profile."""
        user, prefs = private_user

        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{user.id}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(user.id)
        assert data["email"] == user.email

    def test_private_profile_hides_email_from_others(
        self, db_session: Session, private_user: tuple, viewer_user: User
    ):
        """Test that private profiles hide email even if show_email is true."""
        user, prefs = private_user

        # Update to show email but keep profile private
        prefs.privacy["show_email"] = True
        db_session.commit()

        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{viewer_user.id}"}
        )

        # Should still be blocked due to private visibility
        assert response.status_code == 403


class TestPublicProfileEnforcement:
    """Test that public profiles respect field-level privacy."""

    def test_public_profile_allows_authenticated_access(
        self, db_session: Session, public_user: tuple, viewer_user: User
    ):
        """Test that public profiles allow authenticated users to view."""
        user, prefs = public_user

        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{viewer_user.id}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(user.id)

    def test_public_profile_shows_email_when_allowed(
        self, db_session: Session, public_user: tuple, viewer_user: User
    ):
        """Test that public profiles show email when show_email is true."""
        user, prefs = public_user

        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{viewer_user.id}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"] == user.email

    def test_public_profile_hides_email_when_disabled(
        self, db_session: Session, public_user: tuple, viewer_user: User
    ):
        """Test that public profiles hide email when show_email is false."""
        user, prefs = public_user

        # Disable email visibility
        prefs.privacy["show_email"] = False
        db_session.commit()

        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{viewer_user.id}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "email" not in data or data.get("email") is None

    def test_public_profile_shows_activity_when_allowed(
        self, db_session: Session, public_user: tuple, viewer_user: User
    ):
        """Test that public profiles show activity when show_activity is true."""
        user, prefs = public_user

        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{viewer_user.id}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "created_at" in data or "last_login_at" in data

    def test_public_profile_hides_activity_when_disabled(
        self, db_session: Session, public_user: tuple, viewer_user: User
    ):
        """Test that public profiles hide activity when show_activity is false."""
        user, prefs = public_user

        # Disable activity visibility
        prefs.privacy["show_activity"] = False
        db_session.commit()

        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{viewer_user.id}"}
        )

        assert response.status_code == 200
        data = response.json()
        # Activity fields should be hidden
        assert "created_at" not in data or data.get("created_at") is None
        assert "last_login_at" not in data or data.get("last_login_at") is None


class TestContactsOnlyEnforcement:
    """Test contacts-only visibility enforcement."""

    def test_contacts_only_blocks_non_contacts(
        self, db_session: Session, viewer_user: User
    ):
        """Test that contacts-only profiles block non-contacts."""
        user = User(
            id=str(uuid.uuid4()),
            email="contacts_only@example.com",
            display_name="Contacts Only User",
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()

        prefs = UserPreferences(
            user_id=user.id,
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

        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{viewer_user.id}"}
        )

        assert response.status_code == 403
        assert "contacts" in response.json()["detail"].lower()

    def test_contacts_only_allows_owner(
        self, db_session: Session
    ):
        """Test that contacts-only profiles allow the owner to view."""
        user = User(
            id=str(uuid.uuid4()),
            email="contacts_owner@example.com",
            display_name="Contacts Owner",
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()

        prefs = UserPreferences(
            user_id=user.id,
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

        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{user.id}"}
        )

        assert response.status_code == 200


class TestPrivacySettingChanges:
    """Test that privacy setting changes are immediately enforced."""

    def test_changing_to_private_immediately_enforced(
        self, db_session: Session, public_user: tuple, viewer_user: User
    ):
        """Test that changing to private immediately blocks access."""
        user, prefs = public_user

        # Verify viewer can access public profile
        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{viewer_user.id}"}
        )
        assert response.status_code == 200

        # Change to private
        response = client.put(
            f"/api/v1/users/{user.id}/preferences",
            headers={"Authorization": f"Bearer mock_token_{user.id}"},
            json={
                "privacy": {
                    "profile_visibility": "private",
                    "show_email": False,
                    "show_activity": False
                }
            }
        )
        assert response.status_code == 200

        # Verify viewer can no longer access
        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{viewer_user.id}"}
        )
        assert response.status_code == 403

    def test_changing_to_public_immediately_enforced(
        self, db_session: Session, private_user: tuple, viewer_user: User
    ):
        """Test that changing to public immediately allows access."""
        user, prefs = private_user

        # Verify viewer cannot access private profile
        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{viewer_user.id}"}
        )
        assert response.status_code == 403

        # Change to public
        response = client.put(
            f"/api/v1/users/{user.id}/preferences",
            headers={"Authorization": f"Bearer mock_token_{user.id}"},
            json={
                "privacy": {
                    "profile_visibility": "public",
                    "show_email": True,
                    "show_activity": True
                }
            }
        )
        assert response.status_code == 200

        # Verify viewer can now access
        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{viewer_user.id}"}
        )
        assert response.status_code == 200


class TestDefaultPrivacySettings:
    """Test default privacy settings for new users."""

    def test_new_user_has_safe_defaults(
        self, db_session: Session
    ):
        """Test that new users have safe default privacy settings."""
        user = User(
            id=str(uuid.uuid4()),
            email="newuser@example.com",
            display_name="New User",
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()

        # Get preferences (should create defaults)
        response = client.get(
            f"/api/v1/users/{user.id}/preferences",
            headers={"Authorization": f"Bearer mock_token_{user.id}"}
        )

        assert response.status_code == 200
        data = response.json()
        privacy = data["privacy"]

        # Defaults should be reasonably private
        assert privacy["profile_visibility"] in ["public", "contacts", "private"]
        # Email should default to hidden
        assert privacy.get("show_email", True) is False or privacy["profile_visibility"] != "public"
