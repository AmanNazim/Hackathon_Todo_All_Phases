"""
Unit tests for user preferences.

Tests for getting, updating, and validating user preferences.
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
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="prefs_test@example.com",
        display_name="Preferences Test User",
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_preferences(db_session: Session, test_user: User) -> UserPreferences:
    """Create test preferences."""
    prefs = UserPreferences(
        user_id=test_user.id,
        theme="light",
        language="en",
        notifications={
            "email": True,
            "push": False,
            "task_reminders": True,
            "task_assignments": True
        },
        privacy={
            "profile_visibility": "public",
            "show_email": False,
            "show_activity": True
        }
    )
    db_session.add(prefs)
    db_session.commit()
    db_session.refresh(prefs)
    return prefs


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Generate authentication headers."""
    return {"Authorization": f"Bearer mock_token_{test_user.id}"}


class TestPreferencesRetrieval:
    """Test preferences retrieval operations."""

    def test_get_preferences_success(
        self, db_session: Session, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test retrieving user preferences."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "light"
        assert data["language"] == "en"
        assert "notifications" in data
        assert "privacy" in data

    def test_get_preferences_creates_defaults(
        self, db_session: Session, auth_headers: dict
    ):
        """Test that getting preferences creates defaults if none exist."""
        user = User(
            id=str(uuid.uuid4()),
            email="new_user@example.com",
            display_name="New User",
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()

        response = client.get(
            f"/api/v1/users/{user.id}/preferences",
            headers={"Authorization": f"Bearer mock_token_{user.id}"}
        )

        assert response.status_code == 200
        data = response.json()
        # Should have default values
        assert "theme" in data
        assert "language" in data
        assert "notifications" in data
        assert "privacy" in data

    def test_get_preferences_without_auth(self, test_user: User):
        """Test retrieving preferences without authentication."""
        response = client.get(f"/api/v1/users/{test_user.id}/preferences")
        assert response.status_code == 401

    def test_get_other_user_preferences_forbidden(
        self, db_session: Session, test_user: User, test_preferences: UserPreferences
    ):
        """Test that users cannot access other users' preferences."""
        other_user = User(
            id=str(uuid.uuid4()),
            email="other@example.com",
            display_name="Other User",
            created_at=datetime.utcnow()
        )
        db_session.add(other_user)
        db_session.commit()

        response = client.get(
            f"/api/v1/users/{test_user.id}/preferences",
            headers={"Authorization": f"Bearer mock_token_{other_user.id}"}
        )

        assert response.status_code == 403


class TestPreferencesUpdate:
    """Test preferences update operations."""

    def test_update_theme_success(
        self, db_session: Session, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test updating theme preference."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={"theme": "dark"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "dark"

        # Verify in database
        db_session.refresh(test_preferences)
        assert test_preferences.theme == "dark"

    def test_update_language_success(
        self, db_session: Session, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test updating language preference."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={"language": "es"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "es"

    def test_update_notifications_success(
        self, db_session: Session, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test updating notification preferences."""
        new_notifications = {
            "email": False,
            "push": True,
            "task_reminders": False,
            "task_assignments": True
        }
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={"notifications": new_notifications}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["notifications"]["email"] is False
        assert data["notifications"]["push"] is True

    def test_update_privacy_settings_success(
        self, db_session: Session, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test updating privacy settings."""
        new_privacy = {
            "profile_visibility": "private",
            "show_email": True,
            "show_activity": False
        }
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={"privacy": new_privacy}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["privacy"]["profile_visibility"] == "private"
        assert data["privacy"]["show_email"] is True

    def test_update_multiple_preferences(
        self, db_session: Session, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test updating multiple preferences at once."""
        updates = {
            "theme": "dark",
            "language": "fr",
            "notifications": {
                "email": False,
                "push": False,
                "task_reminders": False,
                "task_assignments": False
            }
        }
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json=updates
        )

        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "dark"
        assert data["language"] == "fr"
        assert data["notifications"]["email"] is False

    def test_update_preferences_without_auth(self, test_user: User):
        """Test updating preferences without authentication."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            json={"theme": "dark"}
        )
        assert response.status_code == 401


class TestPreferencesValidation:
    """Test preferences validation."""

    def test_invalid_theme_rejected(
        self, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test that invalid theme values are rejected."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={"theme": "invalid_theme"}
        )

        assert response.status_code == 422

    def test_valid_themes_accepted(
        self, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test that all valid theme values are accepted."""
        valid_themes = ["light", "dark", "system"]

        for theme in valid_themes:
            response = client.put(
                f"/api/v1/users/{test_user.id}/preferences",
                headers=auth_headers,
                json={"theme": theme}
            )
            assert response.status_code == 200
            assert response.json()["theme"] == theme

    def test_invalid_language_rejected(
        self, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test that invalid language codes are rejected."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={"language": "invalid_lang"}
        )

        assert response.status_code == 422

    def test_valid_languages_accepted(
        self, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test that valid language codes are accepted."""
        valid_languages = ["en", "es", "fr", "de", "ja", "zh"]

        for lang in valid_languages:
            response = client.put(
                f"/api/v1/users/{test_user.id}/preferences",
                headers=auth_headers,
                json={"language": lang}
            )
            assert response.status_code == 200
            assert response.json()["language"] == lang

    def test_invalid_visibility_rejected(
        self, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test that invalid visibility values are rejected."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={
                "privacy": {
                    "profile_visibility": "invalid_visibility"
                }
            }
        )

        assert response.status_code == 422

    def test_valid_visibility_levels_accepted(
        self, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test that all valid visibility levels are accepted."""
        valid_levels = ["private", "contacts", "public"]

        for level in valid_levels:
            response = client.put(
                f"/api/v1/users/{test_user.id}/preferences",
                headers=auth_headers,
                json={
                    "privacy": {
                        "profile_visibility": level
                    }
                }
            )
            assert response.status_code == 200
            assert response.json()["privacy"]["profile_visibility"] == level

    def test_notification_settings_boolean_validation(
        self, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test that notification settings must be boolean."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={
                "notifications": {
                    "email": "not_a_boolean"
                }
            }
        )

        assert response.status_code == 422

    def test_privacy_settings_boolean_validation(
        self, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test that privacy boolean settings must be boolean."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={
                "privacy": {
                    "show_email": "not_a_boolean"
                }
            }
        )

        assert response.status_code == 422


class TestNotificationPreferences:
    """Test notification preference handling."""

    def test_disable_all_notifications(
        self, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test disabling all notifications."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={
                "notifications": {
                    "email": False,
                    "push": False,
                    "task_reminders": False,
                    "task_assignments": False
                }
            }
        )

        assert response.status_code == 200
        data = response.json()
        notifications = data["notifications"]
        assert all(value is False for value in notifications.values())

    def test_enable_all_notifications(
        self, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test enabling all notifications."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={
                "notifications": {
                    "email": True,
                    "push": True,
                    "task_reminders": True,
                    "task_assignments": True
                }
            }
        )

        assert response.status_code == 200
        data = response.json()
        notifications = data["notifications"]
        assert all(value is True for value in notifications.values())


class TestPrivacyPreferences:
    """Test privacy preference handling."""

    def test_most_private_settings(
        self, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test setting most private settings."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={
                "privacy": {
                    "profile_visibility": "private",
                    "show_email": False,
                    "show_activity": False
                }
            }
        )

        assert response.status_code == 200
        data = response.json()
        privacy = data["privacy"]
        assert privacy["profile_visibility"] == "private"
        assert privacy["show_email"] is False
        assert privacy["show_activity"] is False

    def test_most_public_settings(
        self, test_user: User, test_preferences: UserPreferences, auth_headers: dict
    ):
        """Test setting most public settings."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={
                "privacy": {
                    "profile_visibility": "public",
                    "show_email": True,
                    "show_activity": True
                }
            }
        )

        assert response.status_code == 200
        data = response.json()
        privacy = data["privacy"]
        assert privacy["profile_visibility"] == "public"
        assert privacy["show_email"] is True
        assert privacy["show_activity"] is True
