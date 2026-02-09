"""
Integration tests for profile error handling.

Tests invalid inputs, missing resources, and edge cases.
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
        email="error_test@example.com",
        display_name="Error Test User",
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Generate authentication headers."""
    return {"Authorization": f"Bearer mock_token_{test_user.id}"}


class TestMissingResourceErrors:
    """Test error handling for missing resources."""

    def test_get_nonexistent_profile(self, auth_headers: dict):
        """Test getting a profile that doesn't exist."""
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/users/{fake_id}/profile",
            headers=auth_headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_nonexistent_profile(self, auth_headers: dict):
        """Test updating a profile that doesn't exist."""
        fake_id = str(uuid.uuid4())
        response = client.put(
            f"/api/v1/users/{fake_id}/profile",
            headers=auth_headers,
            json={"display_name": "New Name"}
        )

        assert response.status_code in [403, 404]

    def test_get_preferences_for_nonexistent_user(self, auth_headers: dict):
        """Test getting preferences for non-existent user."""
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/users/{fake_id}/preferences",
            headers=auth_headers
        )

        assert response.status_code in [403, 404]


class TestInvalidInputErrors:
    """Test error handling for invalid inputs."""

    def test_invalid_user_id_format(self, auth_headers: dict):
        """Test with invalid UUID format."""
        invalid_id = "not-a-valid-uuid"
        response = client.get(
            f"/api/v1/users/{invalid_id}/profile",
            headers=auth_headers
        )

        assert response.status_code in [400, 422]

    def test_empty_request_body(self, test_user: User, auth_headers: dict):
        """Test update with empty request body."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={}
        )

        # Should accept empty body (no changes) or return 422
        assert response.status_code in [200, 422]

    def test_null_values_in_update(self, test_user: User, auth_headers: dict):
        """Test update with null values."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"display_name": None, "bio": None}
        )

        # Should handle null values appropriately
        assert response.status_code in [200, 422]

    def test_wrong_data_types(self, test_user: User, auth_headers: dict):
        """Test with wrong data types."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"display_name": 12345}  # Number instead of string
        )

        assert response.status_code == 422

    def test_invalid_json_format(self, test_user: User, auth_headers: dict):
        """Test with invalid JSON."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers={**auth_headers, "Content-Type": "application/json"},
            data="not valid json"
        )

        assert response.status_code == 422

    def test_missing_content_type(self, test_user: User, auth_headers: dict):
        """Test request without Content-Type header."""
        headers = {k: v for k, v in auth_headers.items()}
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=headers,
            json={"display_name": "Test"}
        )

        # Should still work (FastAPI handles this)
        assert response.status_code == 200


class TestValidationErrors:
    """Test validation error responses."""

    def test_display_name_exceeds_max_length(
        self, test_user: User, auth_headers: dict
    ):
        """Test display name exceeding maximum length."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"display_name": "A" * 200}
        )

        assert response.status_code == 422
        error = response.json()
        assert "detail" in error

    def test_bio_exceeds_max_length(
        self, test_user: User, auth_headers: dict
    ):
        """Test bio exceeding maximum length."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"bio": "A" * 1000}
        )

        assert response.status_code == 422

    def test_invalid_theme_value(
        self, test_user: User, auth_headers: dict
    ):
        """Test invalid theme value."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={"theme": "invalid_theme"}
        )

        assert response.status_code == 422
        error = response.json()
        assert "detail" in error

    def test_invalid_language_code(
        self, test_user: User, auth_headers: dict
    ):
        """Test invalid language code."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={"language": "xyz"}
        )

        assert response.status_code == 422

    def test_invalid_visibility_level(
        self, test_user: User, auth_headers: dict
    ):
        """Test invalid visibility level."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/preferences",
            headers=auth_headers,
            json={
                "privacy": {
                    "profile_visibility": "invalid"
                }
            }
        )

        assert response.status_code == 422


class TestAuthenticationErrors:
    """Test authentication error handling."""

    def test_missing_auth_header(self, test_user: User):
        """Test request without authentication header."""
        response = client.get(f"/api/v1/users/{test_user.id}/profile")

        assert response.status_code == 401
        error = response.json()
        assert "detail" in error

    def test_invalid_auth_token(self, test_user: User):
        """Test with invalid authentication token."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/profile",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    def test_malformed_auth_header(self, test_user: User):
        """Test with malformed authorization header."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/profile",
            headers={"Authorization": "NotBearer token"}
        )

        assert response.status_code == 401

    def test_expired_token(self, test_user: User):
        """Test with expired token (if token expiration is implemented)."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/profile",
            headers={"Authorization": "Bearer expired_token"}
        )

        assert response.status_code == 401


class TestAuthorizationErrors:
    """Test authorization error handling."""

    def test_access_other_user_profile(
        self, db_session: Session, test_user: User, auth_headers: dict
    ):
        """Test accessing another user's profile."""
        other_user = User(
            id=str(uuid.uuid4()),
            email="other@example.com",
            display_name="Other User",
            created_at=datetime.utcnow()
        )
        db_session.add(other_user)
        db_session.commit()

        response = client.put(
            f"/api/v1/users/{other_user.id}/profile",
            headers=auth_headers,
            json={"display_name": "Hacked"}
        )

        assert response.status_code == 403
        error = response.json()
        assert "detail" in error
        assert "forbidden" in error["detail"].lower() or "access denied" in error["detail"].lower()

    def test_access_other_user_preferences(
        self, db_session: Session, test_user: User, auth_headers: dict
    ):
        """Test accessing another user's preferences."""
        other_user = User(
            id=str(uuid.uuid4()),
            email="other2@example.com",
            display_name="Other User 2",
            created_at=datetime.utcnow()
        )
        db_session.add(other_user)
        db_session.commit()

        response = client.get(
            f"/api/v1/users/{other_user.id}/preferences",
            headers=auth_headers
        )

        assert response.status_code == 403


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_unicode_in_display_name(
        self, test_user: User, auth_headers: dict
    ):
        """Test unicode characters in display name."""
        unicode_names = [
            "José García",
            "李明",
            "Müller",
            "Владимир",
            "محمد"
        ]

        for name in unicode_names:
            response = client.put(
                f"/api/v1/users/{test_user.id}/profile",
                headers=auth_headers,
                json={"display_name": name}
            )

            assert response.status_code == 200
            assert response.json()["display_name"] == name

    def test_emoji_in_bio(
        self, test_user: User, auth_headers: dict
    ):
        """Test emoji in bio."""
        bio_with_emoji = "I love coding 💻 and coffee ☕"
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"bio": bio_with_emoji}
        )

        assert response.status_code == 200
        assert response.json()["bio"] == bio_with_emoji

    def test_special_characters_in_fields(
        self, test_user: User, auth_headers: dict
    ):
        """Test special characters in profile fields."""
        special_chars = "Name with @#$%^&*()_+-=[]{}|;:',.<>?/~`"
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"display_name": special_chars}
        )

        # Should handle special characters
        assert response.status_code in [200, 422]

    def test_very_long_valid_bio(
        self, test_user: User, auth_headers: dict
    ):
        """Test bio at maximum allowed length."""
        max_bio = "A" * 500  # Assuming 500 is max
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"bio": max_bio}
        )

        assert response.status_code == 200

    def test_whitespace_only_display_name(
        self, test_user: User, auth_headers: dict
    ):
        """Test display name with only whitespace."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"display_name": "   "}
        )

        # Should either accept or reject, but handle gracefully
        assert response.status_code in [200, 422]

    def test_newlines_in_bio(
        self, test_user: User, auth_headers: dict
    ):
        """Test bio with newline characters."""
        bio_with_newlines = "Line 1\nLine 2\nLine 3"
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"bio": bio_with_newlines}
        )

        assert response.status_code == 200


class TestConcurrentUpdates:
    """Test handling of concurrent updates."""

    def test_rapid_sequential_updates(
        self, test_user: User, auth_headers: dict
    ):
        """Test rapid sequential profile updates."""
        for i in range(10):
            response = client.put(
                f"/api/v1/users/{test_user.id}/profile",
                headers=auth_headers,
                json={"display_name": f"Name {i}"}
            )
            assert response.status_code in [200, 429]  # 429 if rate limited

        # Verify final state
        response = client.get(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers
        )
        assert response.status_code == 200
