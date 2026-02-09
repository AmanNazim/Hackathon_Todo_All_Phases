"""
Integration tests for user login flow.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime


class TestLoginFlow:
    """Test suite for user login integration."""

    def test_login_success(self, client: TestClient, test_user: User, test_user_data: dict):
        """Test successful user login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]

    def test_login_returns_valid_token(self, client: TestClient, test_user: User, test_user_data: dict):
        """Test that login returns a valid JWT token."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )

        assert response.status_code == 200
        token = response.json()["access_token"]

        # Try to use the token
        protected_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert protected_response.status_code == 200

    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Test@Password123"
            }
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_invalid_password(self, client: TestClient, test_user: User):
        """Test login with incorrect password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_case_insensitive_email(self, client: TestClient, test_user: User, test_user_data: dict):
        """Test that login email is case-insensitive."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email.upper(),
                "password": test_user_data["password"]
            }
        )

        assert response.status_code == 200

    def test_login_unverified_email_allowed(self, client: TestClient, unverified_user: User):
        """Test that users with unverified email can still login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": unverified_user.email,
                "password": "Test@Password123"
            }
        )

        # Login should succeed but some operations may be restricted
        assert response.status_code == 200

    def test_login_inactive_user(self, client: TestClient, session: Session):
        """Test that inactive users cannot login."""
        from auth import get_password_hash

        # Create inactive user
        inactive_user = User(
            email="inactive@example.com",
            password_hash=get_password_hash("Test@Password123"),
            first_name="Inactive",
            last_name="User",
            is_active=False
        )
        session.add(inactive_user)
        session.commit()

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "inactive@example.com",
                "password": "Test@Password123"
            }
        )

        assert response.status_code == 401

    def test_login_updates_last_login(self, client: TestClient, session: Session, test_user: User, test_user_data: dict):
        """Test that login updates last_login_at timestamp."""
        # Record time before login
        before_login = datetime.utcnow()

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )

        assert response.status_code == 200

        # Refresh user from database
        session.refresh(test_user)

        # Check that last_login_at was updated
        assert test_user.last_login_at is not None
        assert test_user.last_login_at >= before_login

    def test_login_missing_credentials(self, client: TestClient):
        """Test login with missing credentials."""
        # Missing password
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 422

        # Missing email
        response = client.post(
            "/api/v1/auth/login",
            json={"password": "Test@Password123"}
        )
        assert response.status_code == 422

    def test_login_rate_limiting(self, client: TestClient, test_user: User):
        """Test that failed login attempts are rate limited."""
        # Make multiple failed login attempts
        for _ in range(6):
            client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user.email,
                    "password": "WrongPassword123!"
                }
            )

        # Next attempt should be rate limited
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!"
            }
        )

        # Should be rate limited (429) or account locked (403)
        assert response.status_code in [403, 429]

    def test_login_account_lockout(self, client: TestClient, test_user: User):
        """Test account lockout after multiple failed attempts."""
        # Make 5 failed login attempts
        for _ in range(5):
            client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user.email,
                    "password": "WrongPassword123!"
                }
            )

        # Account should be locked
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": test_user_data["password"]  # Even with correct password
            }
        )

        assert response.status_code == 403
        assert "locked" in response.json()["detail"].lower()

    def test_login_password_not_logged(self, client: TestClient, test_user: User):
        """Test that passwords are not logged or exposed."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "Test@Password123"
            }
        )

        # Response should never contain password
        response_text = response.text.lower()
        assert "test@password123" not in response_text
