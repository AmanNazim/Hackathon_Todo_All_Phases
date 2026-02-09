"""
Integration tests for password reset flow.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from models import User, PasswordResetToken
from auth.tokens import generate_password_reset_token


class TestPasswordResetFlow:
    """Test suite for password reset integration."""

    def test_forgot_password_success(self, client: TestClient, test_user: User):
        """Test successful forgot password request."""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user.email}
        )

        assert response.status_code == 200
        assert "email sent" in response.json()["message"].lower()

    def test_forgot_password_creates_token(self, client: TestClient, session: Session, test_user: User):
        """Test that forgot password creates reset token."""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user.email}
        )

        assert response.status_code == 200

        # Check that token was created
        statement = select(PasswordResetToken).where(
            PasswordResetToken.user_id == test_user.id
        )
        token = session.exec(statement).first()

        assert token is not None
        assert token.used is False

    def test_forgot_password_nonexistent_email(self, client: TestClient):
        """Test forgot password with non-existent email (no enumeration)."""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )

        # Should return success to prevent email enumeration
        assert response.status_code == 200
        assert "email sent" in response.json()["message"].lower()

    def test_forgot_password_invalid_email_format(self, client: TestClient):
        """Test forgot password with invalid email format."""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "notanemail"}
        )

        assert response.status_code == 422

    def test_reset_password_success(self, client: TestClient, session: Session, test_user: User):
        """Test successful password reset."""
        # Generate reset token
        token = generate_password_reset_token(session, test_user.id)

        new_password = "NewPassword123!"
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": new_password
            }
        )

        assert response.status_code == 200
        assert "reset successfully" in response.json()["message"].lower()

    def test_reset_password_can_login_with_new_password(self, client: TestClient, session: Session, test_user: User):
        """Test that user can login with new password after reset."""
        # Generate reset token
        token = generate_password_reset_token(session, test_user.id)

        new_password = "NewPassword123!"
        client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": new_password
            }
        )

        # Try to login with new password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": new_password
            }
        )

        assert response.status_code == 200

    def test_reset_password_old_password_invalid(self, client: TestClient, session: Session, test_user: User, test_user_data: dict):
        """Test that old password no longer works after reset."""
        # Generate reset token
        token = generate_password_reset_token(session, test_user.id)

        new_password = "NewPassword123!"
        client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": new_password
            }
        )

        # Try to login with old password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": test_user_data["password"]
            }
        )

        assert response.status_code == 401

    def test_reset_password_invalid_token(self, client: TestClient):
        """Test password reset with invalid token."""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid_token_12345",
                "new_password": "NewPassword123!"
            }
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    def test_reset_password_expired_token(self, client: TestClient, session: Session, test_user: User):
        """Test password reset with expired token."""
        from datetime import datetime, timedelta

        # Generate token
        token = generate_password_reset_token(session, test_user.id)

        # Manually expire the token
        statement = select(PasswordResetToken).where(
            PasswordResetToken.user_id == test_user.id
        )
        db_token = session.exec(statement).first()
        db_token.expires_at = datetime.utcnow() - timedelta(hours=1)
        session.add(db_token)
        session.commit()

        # Try to reset password
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "NewPassword123!"
            }
        )

        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()

    def test_reset_password_token_single_use(self, client: TestClient, session: Session, test_user: User):
        """Test that reset token can only be used once."""
        token = generate_password_reset_token(session, test_user.id)

        # Use token first time
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "NewPassword123!"
            }
        )
        assert response.status_code == 200

        # Try to use token again
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "AnotherPassword123!"
            }
        )
        assert response.status_code == 400

    def test_reset_password_weak_password(self, client: TestClient, session: Session, test_user: User):
        """Test password reset with weak password."""
        token = generate_password_reset_token(session, test_user.id)

        weak_passwords = [
            "short",
            "nouppercase123!",
            "NOLOWERCASE123!",
            "NoNumbers!",
            "NoSpecial123"
        ]

        for password in weak_passwords:
            response = client.post(
                "/api/v1/auth/reset-password",
                json={
                    "token": token,
                    "new_password": password
                }
            )
            assert response.status_code == 400

    def test_reset_password_rate_limiting(self, client: TestClient):
        """Test that password reset requests are rate limited."""
        # Make multiple reset requests
        for _ in range(6):
            client.post(
                "/api/v1/auth/forgot-password",
                json={"email": "test@example.com"}
            )

        # Next request should be rate limited
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"}
        )

        assert response.status_code == 429
