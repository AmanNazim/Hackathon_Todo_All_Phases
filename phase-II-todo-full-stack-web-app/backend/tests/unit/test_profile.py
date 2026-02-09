"""
Unit tests for profile operations.

Tests for creating, reading, and updating user profiles.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from models import User
from datetime import datetime
import uuid


client = TestClient(app)


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="profile_test@example.com",
        display_name="Profile Test User",
        bio="Original bio",
        avatar_url=None,
        avatar_thumbnail_url=None,
        created_at=datetime.utcnow(),
        last_login_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Generate authentication headers for test user."""
    # Mock JWT token for testing
    return {
        "Authorization": f"Bearer mock_token_{test_user.id}"
    }


class TestProfileRetrieval:
    """Test profile retrieval operations."""

    def test_get_own_profile_success(
        self, db_session: Session, test_user: User, auth_headers: dict
    ):
        """Test retrieving own profile."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["display_name"] == test_user.display_name
        assert data["bio"] == test_user.bio

    def test_get_profile_not_found(self, auth_headers: dict):
        """Test retrieving non-existent profile."""
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/users/{fake_id}/profile",
            headers=auth_headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_profile_without_auth(self, test_user: User):
        """Test retrieving profile without authentication."""
        response = client.get(f"/api/v1/users/{test_user.id}/profile")

        assert response.status_code == 401

    def test_get_profile_includes_completion(
        self, db_session: Session, test_user: User, auth_headers: dict
    ):
        """Test that profile includes completion percentage."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "completion_percentage" in data
        assert isinstance(data["completion_percentage"], (int, float))
        assert 0 <= data["completion_percentage"] <= 100


class TestProfileUpdate:
    """Test profile update operations."""

    def test_update_display_name_success(
        self, db_session: Session, test_user: User, auth_headers: dict
    ):
        """Test updating display name."""
        new_name = "Updated Name"
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"display_name": new_name}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == new_name

        # Verify in database
        db_session.refresh(test_user)
        assert test_user.display_name == new_name

    def test_update_bio_success(
        self, db_session: Session, test_user: User, auth_headers: dict
    ):
        """Test updating bio."""
        new_bio = "This is my updated bio with more information."
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"bio": new_bio}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == new_bio

        # Verify in database
        db_session.refresh(test_user)
        assert test_user.bio == new_bio

    def test_update_multiple_fields(
        self, db_session: Session, test_user: User, auth_headers: dict
    ):
        """Test updating multiple fields at once."""
        updates = {
            "display_name": "New Name",
            "bio": "New bio text"
        }
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json=updates
        )

        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == updates["display_name"]
        assert data["bio"] == updates["bio"]

    def test_update_with_empty_bio(
        self, db_session: Session, test_user: User, auth_headers: dict
    ):
        """Test updating with empty bio (should be allowed)."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"bio": ""}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == ""

    def test_update_display_name_too_long(
        self, test_user: User, auth_headers: dict
    ):
        """Test updating with display name exceeding max length."""
        long_name = "A" * 101  # Assuming max length is 100
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"display_name": long_name}
        )

        assert response.status_code == 422
        assert "validation" in response.json()["detail"].lower() or "length" in str(response.json()).lower()

    def test_update_bio_too_long(
        self, test_user: User, auth_headers: dict
    ):
        """Test updating with bio exceeding max length."""
        long_bio = "A" * 501  # Assuming max length is 500
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"bio": long_bio}
        )

        assert response.status_code == 422

    def test_update_without_auth(self, test_user: User):
        """Test updating profile without authentication."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            json={"display_name": "Hacker"}
        )

        assert response.status_code == 401

    def test_update_other_user_profile(
        self, db_session: Session, test_user: User
    ):
        """Test that users cannot update other users' profiles."""
        other_user = User(
            id=str(uuid.uuid4()),
            email="other@example.com",
            display_name="Other User",
            created_at=datetime.utcnow()
        )
        db_session.add(other_user)
        db_session.commit()

        # Try to update other user's profile with test_user's token
        auth_headers = {"Authorization": f"Bearer mock_token_{test_user.id}"}
        response = client.put(
            f"/api/v1/users/{other_user.id}/profile",
            headers=auth_headers,
            json={"display_name": "Hacked Name"}
        )

        assert response.status_code == 403
        assert "access denied" in response.json()["detail"].lower() or "forbidden" in response.json()["detail"].lower()


class TestProfileValidation:
    """Test profile input validation."""

    def test_xss_prevention_in_display_name(
        self, test_user: User, auth_headers: dict
    ):
        """Test that XSS attempts in display name are sanitized."""
        xss_name = "<script>alert('xss')</script>"
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"display_name": xss_name}
        )

        # Should either reject or sanitize
        if response.status_code == 200:
            data = response.json()
            assert "<script>" not in data["display_name"]
        else:
            assert response.status_code == 422

    def test_xss_prevention_in_bio(
        self, test_user: User, auth_headers: dict
    ):
        """Test that XSS attempts in bio are sanitized."""
        xss_bio = "My bio <script>alert('xss')</script> is here"
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"bio": xss_bio}
        )

        # Should either reject or sanitize
        if response.status_code == 200:
            data = response.json()
            assert "<script>" not in data["bio"]
        else:
            assert response.status_code == 422

    def test_sql_injection_prevention(
        self, test_user: User, auth_headers: dict
    ):
        """Test that SQL injection attempts are prevented."""
        sql_injection = "'; DROP TABLE users; --"
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"display_name": sql_injection}
        )

        # Should handle safely (either accept as string or reject)
        assert response.status_code in [200, 422]


class TestProfileCompletion:
    """Test profile completion tracking."""

    def test_empty_profile_low_completion(
        self, db_session: Session, auth_headers: dict
    ):
        """Test that empty profile has low completion percentage."""
        user = User(
            id=str(uuid.uuid4()),
            email="empty@example.com",
            display_name=None,
            bio=None,
            avatar_url=None,
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()

        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{user.id}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completion_percentage"] < 50

    def test_complete_profile_high_completion(
        self, db_session: Session, auth_headers: dict
    ):
        """Test that complete profile has high completion percentage."""
        user = User(
            id=str(uuid.uuid4()),
            email="complete@example.com",
            display_name="Complete User",
            bio="I have a complete profile with all fields filled.",
            avatar_url="https://example.com/avatar.jpg",
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()

        response = client.get(
            f"/api/v1/users/{user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{user.id}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completion_percentage"] >= 75
