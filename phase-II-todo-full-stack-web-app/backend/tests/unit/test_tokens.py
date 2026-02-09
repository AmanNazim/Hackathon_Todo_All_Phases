"""
Unit tests for password reset and email verification tokens.
"""

import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select
from auth.tokens import (
    generate_password_reset_token,
    verify_password_reset_token,
    generate_email_verification_token,
    verify_email_verification_token
)
from models import User, PasswordResetToken, EmailVerificationToken


class TestPasswordResetTokens:
    """Test suite for password reset token generation and verification."""

    def test_generate_reset_token_creates_token(self, session: Session, test_user: User):
        """Test that password reset token is created successfully."""
        token = generate_password_reset_token(session, test_user.id)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_reset_token_stores_in_database(self, session: Session, test_user: User):
        """Test that reset token is stored in database."""
        token = generate_password_reset_token(session, test_user.id)

        # Check database
        statement = select(PasswordResetToken).where(
            PasswordResetToken.user_id == test_user.id
        )
        db_token = session.exec(statement).first()

        assert db_token is not None
        assert db_token.user_id == test_user.id
        assert db_token.used is False

    def test_generate_reset_token_has_expiration(self, session: Session, test_user: User):
        """Test that reset token has expiration time."""
        token = generate_password_reset_token(session, test_user.id)

        statement = select(PasswordResetToken).where(
            PasswordResetToken.user_id == test_user.id
        )
        db_token = session.exec(statement).first()

        assert db_token.expires_at is not None
        # Should expire in approximately 1 hour
        time_diff = (db_token.expires_at - datetime.utcnow()).total_seconds()
        assert 3500 < time_diff < 3700  # Allow 100 second margin

    def test_verify_reset_token_valid(self, session: Session, test_user: User):
        """Test verification of valid reset token."""
        token = generate_password_reset_token(session, test_user.id)

        user_id = verify_password_reset_token(session, token)
        assert user_id == test_user.id

    def test_verify_reset_token_invalid(self, session: Session):
        """Test that invalid token is rejected."""
        invalid_token = "invalid_token_12345"

        user_id = verify_password_reset_token(session, invalid_token)
        assert user_id is None

    def test_verify_reset_token_expired(self, session: Session, test_user: User):
        """Test that expired token is rejected."""
        # Create token
        token = generate_password_reset_token(session, test_user.id)

        # Manually expire the token
        statement = select(PasswordResetToken).where(
            PasswordResetToken.user_id == test_user.id
        )
        db_token = session.exec(statement).first()
        db_token.expires_at = datetime.utcnow() - timedelta(hours=1)
        session.add(db_token)
        session.commit()

        # Verify should fail
        user_id = verify_password_reset_token(session, token)
        assert user_id is None

    def test_verify_reset_token_already_used(self, session: Session, test_user: User):
        """Test that used token is rejected."""
        token = generate_password_reset_token(session, test_user.id)

        # Use the token once
        user_id = verify_password_reset_token(session, token)
        assert user_id == test_user.id

        # Try to use again - should fail
        user_id = verify_password_reset_token(session, token)
        assert user_id is None

    def test_generate_multiple_tokens_invalidates_old(self, session: Session, test_user: User):
        """Test that generating new token invalidates old ones."""
        token1 = generate_password_reset_token(session, test_user.id)
        token2 = generate_password_reset_token(session, test_user.id)

        # Old token should be invalid
        user_id = verify_password_reset_token(session, token1)
        assert user_id is None

        # New token should be valid
        user_id = verify_password_reset_token(session, token2)
        assert user_id == test_user.id


class TestEmailVerificationTokens:
    """Test suite for email verification token generation and verification."""

    def test_generate_verification_token_creates_token(self, session: Session, test_user: User):
        """Test that email verification token is created successfully."""
        token = generate_email_verification_token(session, test_user.id)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_verification_token_stores_in_database(self, session: Session, test_user: User):
        """Test that verification token is stored in database."""
        token = generate_email_verification_token(session, test_user.id)

        # Check database
        statement = select(EmailVerificationToken).where(
            EmailVerificationToken.user_id == test_user.id
        )
        db_token = session.exec(statement).first()

        assert db_token is not None
        assert db_token.user_id == test_user.id
        assert db_token.used is False

    def test_generate_verification_token_has_expiration(self, session: Session, test_user: User):
        """Test that verification token has expiration time."""
        token = generate_email_verification_token(session, test_user.id)

        statement = select(EmailVerificationToken).where(
            EmailVerificationToken.user_id == test_user.id
        )
        db_token = session.exec(statement).first()

        assert db_token.expires_at is not None
        # Should expire in approximately 24 hours
        time_diff = (db_token.expires_at - datetime.utcnow()).total_seconds()
        assert 86000 < time_diff < 87000  # Allow margin

    def test_verify_verification_token_valid(self, session: Session, test_user: User):
        """Test verification of valid email verification token."""
        token = generate_email_verification_token(session, test_user.id)

        user_id = verify_email_verification_token(session, token)
        assert user_id == test_user.id

    def test_verify_verification_token_invalid(self, session: Session):
        """Test that invalid verification token is rejected."""
        invalid_token = "invalid_token_12345"

        user_id = verify_email_verification_token(session, invalid_token)
        assert user_id is None

    def test_verify_verification_token_expired(self, session: Session, test_user: User):
        """Test that expired verification token is rejected."""
        token = generate_email_verification_token(session, test_user.id)

        # Manually expire the token
        statement = select(EmailVerificationToken).where(
            EmailVerificationToken.user_id == test_user.id
        )
        db_token = session.exec(statement).first()
        db_token.expires_at = datetime.utcnow() - timedelta(hours=1)
        session.add(db_token)
        session.commit()

        # Verify should fail
        user_id = verify_email_verification_token(session, token)
        assert user_id is None

    def test_verify_verification_token_already_used(self, session: Session, test_user: User):
        """Test that used verification token is rejected."""
        token = generate_email_verification_token(session, test_user.id)

        # Use the token once
        user_id = verify_email_verification_token(session, token)
        assert user_id == test_user.id

        # Try to use again - should fail
        user_id = verify_email_verification_token(session, token)
        assert user_id is None
