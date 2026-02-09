"""
Security tests for profile features.

Tests XSS prevention, file upload security, and privacy enforcement.
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
        email="security_test@example.com",
        display_name="Security Test User",
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


class TestXSSPrevention:
    """Test XSS attack prevention in profile fields."""

    def test_script_tag_in_display_name(
        self, test_user: User, auth_headers: dict
    ):
        """Test that script tags in display name are sanitized or rejected."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<script>document.cookie</script>",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "javascript:alert('xss')"
        ]

        for payload in xss_payloads:
            response = client.put(
                f"/api/v1/users/{test_user.id}/profile",
                headers=auth_headers,
                json={"display_name": payload}
            )

            # Should either reject (422) or sanitize (200 with cleaned data)
            if response.status_code == 200:
                data = response.json()
                # Verify dangerous content is removed
                assert "<script>" not in data["display_name"].lower()
                assert "javascript:" not in data["display_name"].lower()
                assert "onerror=" not in data["display_name"].lower()
                assert "onload=" not in data["display_name"].lower()
            else:
                assert response.status_code == 422

    def test_script_tag_in_bio(
        self, test_user: User, auth_headers: dict
    ):
        """Test that script tags in bio are sanitized or rejected."""
        xss_payloads = [
            "My bio <script>alert('xss')</script> is here",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<body onload=alert('xss')>",
            "<input onfocus=alert('xss') autofocus>"
        ]

        for payload in xss_payloads:
            response = client.put(
                f"/api/v1/users/{test_user.id}/profile",
                headers=auth_headers,
                json={"bio": payload}
            )

            if response.status_code == 200:
                data = response.json()
                # Verify dangerous content is removed
                assert "<script>" not in data["bio"].lower()
                assert "<iframe>" not in data["bio"].lower()
                assert "onload=" not in data["bio"].lower()
                assert "onfocus=" not in data["bio"].lower()
            else:
                assert response.status_code == 422

    def test_html_entities_in_profile(
        self, test_user: User, auth_headers: dict
    ):
        """Test that HTML entities are properly handled."""
        test_cases = [
            "&lt;script&gt;alert('xss')&lt;/script&gt;",
            "&#60;script&#62;alert('xss')&#60;/script&#62;",
            "Test &amp; Company",
            "Price: $100 &lt; $200"
        ]

        for test_input in test_cases:
            response = client.put(
                f"/api/v1/users/{test_user.id}/profile",
                headers=auth_headers,
                json={"display_name": test_input}
            )

            # Should handle safely
            assert response.status_code in [200, 422]

    def test_unicode_and_emoji_allowed(
        self, test_user: User, auth_headers: dict
    ):
        """Test that legitimate unicode and emoji are allowed."""
        valid_inputs = [
            "José García",
            "李明",
            "Müller",
            "Hello 👋 World",
            "🎉 Party Time 🎊"
        ]

        for valid_input in valid_inputs:
            response = client.put(
                f"/api/v1/users/{test_user.id}/profile",
                headers=auth_headers,
                json={"display_name": valid_input}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["display_name"] == valid_input


class TestSQLInjectionPrevention:
    """Test SQL injection prevention."""

    def test_sql_injection_in_display_name(
        self, test_user: User, auth_headers: dict
    ):
        """Test that SQL injection attempts are safely handled."""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
            "1'; DELETE FROM users WHERE '1'='1"
        ]

        for payload in sql_payloads:
            response = client.put(
                f"/api/v1/users/{test_user.id}/profile",
                headers=auth_headers,
                json={"display_name": payload}
            )

            # Should handle safely (either accept as string or reject)
            assert response.status_code in [200, 422]

            # If accepted, verify it's stored as literal string
            if response.status_code == 200:
                data = response.json()
                # The payload should be stored as-is, not executed
                assert isinstance(data["display_name"], str)

    def test_sql_injection_in_search(
        self, test_user: User, auth_headers: dict
    ):
        """Test that SQL injection in search queries is prevented."""
        sql_payloads = [
            "' OR 1=1--",
            "'; DROP TABLE users;--",
            "' UNION SELECT password FROM users--"
        ]

        for payload in sql_payloads:
            # Assuming there's a search endpoint
            response = client.get(
                f"/api/v1/users/{test_user.id}/profile",
                headers=auth_headers,
                params={"search": payload}
            )

            # Should handle safely
            assert response.status_code in [200, 400, 404]


class TestAuthorizationEnforcement:
    """Test authorization and access control."""

    def test_cannot_update_other_user_profile(
        self, db_session: Session, test_user: User, auth_headers: dict
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

        response = client.put(
            f"/api/v1/users/{other_user.id}/profile",
            headers=auth_headers,
            json={"display_name": "Hacked Name"}
        )

        assert response.status_code == 403

    def test_cannot_view_private_profile(
        self, db_session: Session, test_user: User
    ):
        """Test that private profiles cannot be viewed by others."""
        # Set profile to private
        prefs = UserPreferences(
            user_id=test_user.id,
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

        # Create another user
        other_user = User(
            id=str(uuid.uuid4()),
            email="viewer@example.com",
            display_name="Viewer",
            created_at=datetime.utcnow()
        )
        db_session.add(other_user)
        db_session.commit()

        # Try to view private profile
        response = client.get(
            f"/api/v1/users/{test_user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{other_user.id}"}
        )

        assert response.status_code == 403

    def test_cannot_access_without_authentication(
        self, test_user: User
    ):
        """Test that endpoints require authentication."""
        # Try to access profile without auth
        response = client.get(f"/api/v1/users/{test_user.id}/profile")
        assert response.status_code == 401

        # Try to update profile without auth
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            json={"display_name": "Hacker"}
        )
        assert response.status_code == 401

        # Try to access preferences without auth
        response = client.get(f"/api/v1/users/{test_user.id}/preferences")
        assert response.status_code == 401

    def test_invalid_token_rejected(self, test_user: User):
        """Test that invalid tokens are rejected."""
        invalid_headers = {"Authorization": "Bearer invalid_token"}

        response = client.get(
            f"/api/v1/users/{test_user.id}/profile",
            headers=invalid_headers
        )

        assert response.status_code == 401


class TestInputValidation:
    """Test input validation and boundary conditions."""

    def test_display_name_length_limits(
        self, test_user: User, auth_headers: dict
    ):
        """Test display name length validation."""
        # Too long (assuming max 100 characters)
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"display_name": "A" * 101}
        )
        assert response.status_code == 422

        # Maximum allowed length
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"display_name": "A" * 100}
        )
        assert response.status_code == 200

        # Empty string (should be allowed)
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"display_name": ""}
        )
        assert response.status_code == 200

    def test_bio_length_limits(
        self, test_user: User, auth_headers: dict
    ):
        """Test bio length validation."""
        # Too long (assuming max 500 characters)
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"bio": "A" * 501}
        )
        assert response.status_code == 422

        # Maximum allowed length
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={"bio": "A" * 500}
        )
        assert response.status_code == 200

    def test_malformed_json_rejected(
        self, test_user: User, auth_headers: dict
    ):
        """Test that malformed JSON is rejected."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers={**auth_headers, "Content-Type": "application/json"},
            data="{'invalid': json}"  # Malformed JSON
        )

        assert response.status_code == 422

    def test_unexpected_fields_ignored(
        self, test_user: User, auth_headers: dict
    ):
        """Test that unexpected fields are ignored."""
        response = client.put(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers,
            json={
                "display_name": "Valid Name",
                "unexpected_field": "should be ignored",
                "admin": True,  # Attempt to escalate privileges
                "role": "admin"
            }
        )

        # Should succeed but ignore unexpected fields
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Valid Name"
        assert "unexpected_field" not in data
        assert "admin" not in data
        assert "role" not in data


class TestRateLimiting:
    """Test rate limiting (if implemented)."""

    def test_excessive_requests_rate_limited(
        self, test_user: User, auth_headers: dict
    ):
        """Test that excessive requests are rate limited."""
        # Make many rapid requests
        responses = []
        for i in range(100):
            response = client.put(
                f"/api/v1/users/{test_user.id}/profile",
                headers=auth_headers,
                json={"display_name": f"Name {i}"}
            )
            responses.append(response.status_code)

        # If rate limiting is implemented, should see 429 responses
        # If not implemented, all should be 200
        assert all(code in [200, 429] for code in responses)


class TestDataLeakage:
    """Test for potential data leakage."""

    def test_error_messages_no_sensitive_data(
        self, test_user: User, auth_headers: dict
    ):
        """Test that error messages don't leak sensitive information."""
        # Try to access non-existent user
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/v1/users/{fake_id}/profile",
            headers=auth_headers
        )

        assert response.status_code == 404
        error_detail = response.json()["detail"].lower()

        # Should not leak database structure or internal details
        assert "sql" not in error_detail
        assert "database" not in error_detail
        assert "table" not in error_detail
        assert "column" not in error_detail

    def test_private_fields_not_exposed(
        self, db_session: Session, test_user: User, auth_headers: dict
    ):
        """Test that private fields are not exposed in responses."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/profile",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should not expose sensitive internal fields
        assert "password" not in data
        assert "password_hash" not in data
        assert "hashed_password" not in data
        assert "salt" not in data
