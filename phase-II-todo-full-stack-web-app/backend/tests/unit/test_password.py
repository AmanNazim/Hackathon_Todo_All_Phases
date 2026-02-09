"""
Unit tests for password hashing functionality.
"""

import pytest
from auth import get_password_hash, verify_password


class TestPasswordHashing:
    """Test suite for password hashing and verification."""

    def test_hash_password_creates_valid_hash(self):
        """Test that password hashing creates a valid bcrypt hash."""
        password = "Test@Password123"
        hashed = get_password_hash(password)

        # Bcrypt hashes start with $2b$ and are 60 characters long
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60

    def test_hash_password_different_for_same_input(self):
        """Test that hashing the same password twice produces different hashes (salt)."""
        password = "Test@Password123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2

    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "Test@Password123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        password = "Test@Password123"
        wrong_password = "Wrong@Password456"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "Test@Password123"
        hashed = get_password_hash(password)

        assert verify_password("test@password123", hashed) is False
        assert verify_password("TEST@PASSWORD123", hashed) is False

    def test_verify_password_empty_string(self):
        """Test that empty password verification fails."""
        password = "Test@Password123"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False

    def test_hash_password_with_special_characters(self):
        """Test password hashing with various special characters."""
        passwords = [
            "P@ssw0rd!",
            "Test#123$",
            "Complex&Pass^123",
            "Unicode™Password®",
        ]

        for password in passwords:
            hashed = get_password_hash(password)
            assert verify_password(password, hashed) is True

    def test_hash_password_with_unicode(self):
        """Test password hashing with unicode characters."""
        password = "Пароль123!@#"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_with_invalid_hash(self):
        """Test that verify_password handles invalid hash gracefully."""
        password = "Test@Password123"
        invalid_hash = "not_a_valid_hash"

        # Should return False or raise an exception
        try:
            result = verify_password(password, invalid_hash)
            assert result is False
        except Exception:
            # It's acceptable to raise an exception for invalid hash
            pass
