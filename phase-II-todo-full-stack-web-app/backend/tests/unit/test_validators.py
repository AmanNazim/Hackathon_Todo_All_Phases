"""
Unit tests for authentication validators.
"""

import pytest
from validators.auth import (
    validate_email,
    validate_password,
    validate_name,
    AuthValidationError
)


class TestEmailValidation:
    """Test suite for email validation."""

    def test_validate_email_valid(self):
        """Test validation of valid email addresses."""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
            "user123@test-domain.com"
        ]

        for email in valid_emails:
            # Should not raise exception
            validate_email(email)

    def test_validate_email_invalid_format(self):
        """Test validation of invalid email formats."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com",
            ""
        ]

        for email in invalid_emails:
            with pytest.raises(AuthValidationError):
                validate_email(email)

    def test_validate_email_normalizes_case(self):
        """Test that email validation normalizes to lowercase."""
        email = "User@Example.COM"
        normalized = validate_email(email)
        assert normalized == "user@example.com"


class TestPasswordValidation:
    """Test suite for password validation."""

    def test_validate_password_valid(self):
        """Test validation of valid passwords."""
        valid_passwords = [
            "Test@Password123",
            "Complex!Pass1",
            "Str0ng#Pwd",
            "MyP@ssw0rd"
        ]

        for password in valid_passwords:
            # Should not raise exception
            validate_password(password)

    def test_validate_password_too_short(self):
        """Test that short passwords are rejected."""
        with pytest.raises(AuthValidationError) as exc_info:
            validate_password("Short1!")
        assert "8 characters" in str(exc_info.value)

    def test_validate_password_no_uppercase(self):
        """Test that passwords without uppercase are rejected."""
        with pytest.raises(AuthValidationError) as exc_info:
            validate_password("nouppercase123!")
        assert "uppercase" in str(exc_info.value).lower()

    def test_validate_password_no_lowercase(self):
        """Test that passwords without lowercase are rejected."""
        with pytest.raises(AuthValidationError) as exc_info:
            validate_password("NOLOWERCASE123!")
        assert "lowercase" in str(exc_info.value).lower()

    def test_validate_password_no_digit(self):
        """Test that passwords without digits are rejected."""
        with pytest.raises(AuthValidationError) as exc_info:
            validate_password("NoDigits!@#")
        assert "digit" in str(exc_info.value).lower()

    def test_validate_password_no_special_char(self):
        """Test that passwords without special characters are rejected."""
        with pytest.raises(AuthValidationError) as exc_info:
            validate_password("NoSpecial123")
        assert "special" in str(exc_info.value).lower()

    def test_validate_password_common_passwords(self):
        """Test that common passwords are rejected."""
        common_passwords = [
            "Password123!",
            "Welcome123!",
            "Admin123!",
            "Qwerty123!"
        ]

        for password in common_passwords:
            with pytest.raises(AuthValidationError):
                validate_password(password)


class TestNameValidation:
    """Test suite for name validation."""

    def test_validate_name_valid(self):
        """Test validation of valid names."""
        valid_names = [
            "John",
            "Mary Jane",
            "O'Brien",
            "Jean-Pierre",
            "José"
        ]

        for name in valid_names:
            # Should not raise exception
            validate_name(name)

    def test_validate_name_empty(self):
        """Test that empty names are rejected."""
        with pytest.raises(AuthValidationError):
            validate_name("")

    def test_validate_name_too_short(self):
        """Test that single character names are rejected."""
        with pytest.raises(AuthValidationError):
            validate_name("A")

    def test_validate_name_with_numbers(self):
        """Test that names with numbers are rejected."""
        with pytest.raises(AuthValidationError):
            validate_name("John123")

    def test_validate_name_with_special_chars(self):
        """Test that names with invalid special characters are rejected."""
        invalid_names = [
            "John@Doe",
            "Mary#Jane",
            "Test$User"
        ]

        for name in invalid_names:
            with pytest.raises(AuthValidationError):
                validate_name(name)

    def test_validate_name_too_long(self):
        """Test that excessively long names are rejected."""
        long_name = "A" * 101
        with pytest.raises(AuthValidationError):
            validate_name(long_name)

    def test_validate_name_normalizes_whitespace(self):
        """Test that name validation normalizes whitespace."""
        name = "  John   Doe  "
        normalized = validate_name(name)
        assert normalized == "John Doe"
