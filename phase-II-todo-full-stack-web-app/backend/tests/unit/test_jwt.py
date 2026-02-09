"""
Unit tests for JWT token generation and verification.
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError
from auth import create_access_token, verify_token, SECRET_KEY, ALGORITHM


class TestJWTTokens:
    """Test suite for JWT token generation and verification."""

    def test_create_access_token_basic(self):
        """Test basic JWT token creation."""
        data = {"sub": "user123"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_subject(self):
        """Test that created token contains the subject."""
        user_id = "user123"
        data = {"sub": user_id}
        token = create_access_token(data)

        # Decode without verification to check contents
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == user_id

    def test_create_access_token_has_expiration(self):
        """Test that created token has expiration time."""
        data = {"sub": "user123"}
        token = create_access_token(data)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)

    def test_create_access_token_custom_expiration(self):
        """Test token creation with custom expiration time."""
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=5)
        token = create_access_token(data, expires_delta=expires_delta)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()

        # Should expire in approximately 5 minutes
        time_diff = (exp_time - now).total_seconds()
        assert 290 < time_diff < 310  # Allow 10 second margin

    def test_create_access_token_with_additional_claims(self):
        """Test token creation with additional claims."""
        data = {
            "sub": "user123",
            "email": "test@example.com",
            "role": "admin"
        }
        token = create_access_token(data)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"
        assert decoded["role"] == "admin"

    def test_verify_token_valid(self):
        """Test verification of valid token."""
        data = {"sub": "user123"}
        token = create_access_token(data)

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"

    def test_verify_token_invalid_signature(self):
        """Test that token with invalid signature is rejected."""
        data = {"sub": "user123"}
        token = create_access_token(data)

        # Tamper with the token
        tampered_token = token[:-10] + "tampered00"

        payload = verify_token(tampered_token)
        assert payload is None

    def test_verify_token_expired(self):
        """Test that expired token is rejected."""
        data = {"sub": "user123"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expires_delta)

        payload = verify_token(token)
        assert payload is None

    def test_verify_token_malformed(self):
        """Test that malformed token is rejected."""
        malformed_tokens = [
            "not.a.token",
            "invalid",
            "",
            "a.b",  # Only 2 parts instead of 3
        ]

        for token in malformed_tokens:
            payload = verify_token(token)
            assert payload is None

    def test_verify_token_wrong_algorithm(self):
        """Test that token signed with wrong algorithm is rejected."""
        data = {"sub": "user123", "exp": datetime.utcnow() + timedelta(minutes=30)}
        # Sign with different algorithm
        token = jwt.encode(data, SECRET_KEY, algorithm="HS512")

        payload = verify_token(token)
        assert payload is None

    def test_token_roundtrip(self):
        """Test complete token creation and verification cycle."""
        original_data = {
            "sub": "user123",
            "email": "test@example.com",
            "name": "Test User"
        }

        token = create_access_token(original_data)
        verified_data = verify_token(token)

        assert verified_data is not None
        assert verified_data["sub"] == original_data["sub"]
        assert verified_data["email"] == original_data["email"]
        assert verified_data["name"] == original_data["name"]

    def test_create_multiple_tokens_different(self):
        """Test that creating multiple tokens produces different results."""
        data = {"sub": "user123"}

        token1 = create_access_token(data)
        token2 = create_access_token(data)

        # Tokens should be different due to different exp times
        assert token1 != token2
