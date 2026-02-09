"""
Integration tests for email verification flow.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from models import User, EmailVerificationToken
from auth.tokens import generate_email_verification_token


class TestEmailVerificationFlow:
    """Test suite for email verification integration."""

    def test_verify_email_success(self, client: TestClient, session: Session, unverified_user: User):
        """Test successful email verification."""
        # Generate verification token
        token = generate_email_verification_token(session, unverified_user.id)

        response = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token}
        )

        assert response.status_code == 200
        assert "verified successfully" in response.json()["message"].lower()

    def test_verify_email_updates_user_status(self, client: TestClient, session: Session, unverified_user: User):
        """Test that email verification updates user's email_verified status."""
        # Generate verification token
        token = generate_email_verification_token(session, unverified_user.id)

        # Verify email
        client.post(
            "/api/v1/auth/verify-email",
            json={"token": token}
        )

        # Refresh user from database
        session.refresh(unverified_user)

        assert unverified_user.email_verified is True

    def test_verify_email_invalid_token(self, client: TestClient):
        """Test email verification with invalid token."""
        response = client.post(
            "/api/v1/auth/verify-email",
            json={"token": "invalid_token_12345"}
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    def test_verify_email_expired_token(self, client: TestClient, session: Session, unverified_user: User):
        """Test email verification with expired token."""
        from datetime import datetime, timedelta

        # Generate token
        token = generate_email_verification_token(session, unverified_user.id)

        # Manually expire the token
        statement = select(EmailVerificationToken).where(
            EmailVerificationToken.user_id == unverified_user.id
        )
        db_token = session.exec(statement).first()
        db_token.expires_at = datetime.utcnow() - timedelta(hours=1)
        session.add(db_token)
        session.commit()

        # Try to verify
        response = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token}
        )

        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()

    def test_verify_email_already_verified(self, client: TestClient, session: Session, test_user: User):
        """Test verifying email that's already verified."""
        # Generate token for already verified user
        token = generate_email_verification_token(session, test_user.id)

        response = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token}
        )

        # Should succeed (idempotent operation)
        assert response.status_code == 200

    def test_verify_email_token_single_use(self, client: TestClient, session: Session, unverified_user: User):
        """Test that verification token can only be used once."""
        token = generate_email_verification_token(session, unverified_user.id)

        # Use token first time
        response = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token}
        )
        assert response.status_code == 200

        # Try to use token again
        response = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token}
        )
        assert response.status_code == 400

    def test_resend_verification_email_success(self, client: TestClient, unverified_user: User, auth_headers: dict):
        """Test successful resend of verification email."""
        response = client.post(
            "/api/v1/auth/resend-verification",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert "sent" in response.json()["message"].lower()

    def test_resend_verification_creates_new_token(self, client: TestClient, session: Session, unverified_user: User):
        """Test that resending verification creates a new token."""
        from auth import create_access_token

        # Create auth headers for unverified user
        token = create_access_token({"sub": str(unverified_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        # Get initial token count
        statement = select(EmailVerificationToken).where(
            EmailVerificationToken.user_id == unverified_user.id
        )
        initial_tokens = session.exec(statement).all()
        initial_count = len(initial_tokens)

        # Resend verification
        client.post(
            "/api/v1/auth/resend-verification",
            headers=headers
        )

        # Check that new token was created
        new_tokens = session.exec(statement).all()
        assert len(new_tokens) > initial_count

    def test_resend_verification_requires_authentication(self, client: TestClient):
        """Test that resending verification requires authentication."""
        response = client.post("/api/v1/auth/resend-verification")

        assert response.status_code == 401

    def test_resend_verification_already_verified(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test resending verification for already verified user."""
        response = client.post(
            "/api/v1/auth/resend-verification",
            headers=auth_headers
        )

        # Should return appropriate message
        assert response.status_code in [200, 400]

    def test_resend_verification_rate_limiting(self, client: TestClient, unverified_user: User):
        """Test that resend verification is rate limited."""
        from auth import create_access_token

        token = create_access_token({"sub": str(unverified_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        # Make multiple resend requests
        for _ in range(6):
            client.post(
                "/api/v1/auth/resend-verification",
                headers=headers
            )

        # Next request should be rate limited
        response = client.post(
            "/api/v1/auth/resend-verification",
            headers=headers
        )

        assert response.status_code == 429

    def test_verified_email_required_for_sensitive_operations(self, client: TestClient, session: Session, unverified_user: User):
        """Test that sensitive operations require verified email."""
        from auth import create_access_token

        # Create auth headers for unverified user
        token = create_access_token({"sub": str(unverified_user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        # Try to perform sensitive operation (e.g., change password)
        response = client.post(
            "/api/v1/auth/change-password",
            headers=headers,
            json={
                "current_password": "Test@Password123",
                "new_password": "NewPassword123!"
            }
        )

        # Should be forbidden due to unverified email
        assert response.status_code == 403
        assert "verify" in response.json()["detail"].lower()
