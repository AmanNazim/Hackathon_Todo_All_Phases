"""
Integration tests for user registration flow.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from models import User, EmailVerificationToken


class TestRegistrationFlow:
    """Test suite for user registration integration."""

    def test_register_success(self, client: TestClient, session: Session):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Test@Password123",
                "first_name": "New",
                "last_name": "User"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["first_name"] == "New"
        assert data["last_name"] == "User"
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_creates_user_in_database(self, client: TestClient, session: Session):
        """Test that registration creates user in database."""
        email = "dbuser@example.com"
        client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "Test@Password123",
                "first_name": "DB",
                "last_name": "User"
            }
        )

        # Check database
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        assert user is not None
        assert user.email == email
        assert user.first_name == "DB"
        assert user.last_name == "User"
        assert user.email_verified is False
        assert user.is_active is True

    def test_register_sends_verification_email(self, client: TestClient, session: Session):
        """Test that registration triggers verification email."""
        email = "verify@example.com"
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "Test@Password123",
                "first_name": "Verify",
                "last_name": "User"
            }
        )

        assert response.status_code == 201

        # Check that verification token was created
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        token_statement = select(EmailVerificationToken).where(
            EmailVerificationToken.user_id == user.id
        )
        token = session.exec(token_statement).first()

        assert token is not None
        assert token.used is False

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test that registering with duplicate email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "Test@Password123",
                "first_name": "Duplicate",
                "last_name": "User"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email_format(self, client: TestClient):
        """Test registration with invalid email format."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            ""
        ]

        for email in invalid_emails:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "Test@Password123",
                    "first_name": "Test",
                    "last_name": "User"
                }
            )
            assert response.status_code == 422

    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password."""
        weak_passwords = [
            "short",
            "nouppercase123!",
            "NOLOWERCASE123!",
            "NoNumbers!",
            "NoSpecial123"
        ]

        for password in weak_passwords:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "password": password,
                    "first_name": "Test",
                    "last_name": "User"
                }
            )
            assert response.status_code == 400

    def test_register_missing_required_fields(self, client: TestClient):
        """Test registration with missing required fields."""
        # Missing email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "password": "Test@Password123",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        assert response.status_code == 422

        # Missing password
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        assert response.status_code == 422

    def test_register_password_not_returned(self, client: TestClient):
        """Test that password is never returned in response."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "secure@example.com",
                "password": "Test@Password123",
                "first_name": "Secure",
                "last_name": "User"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_name_validation(self, client: TestClient):
        """Test name validation during registration."""
        # Empty names
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test@Password123",
                "first_name": "",
                "last_name": "User"
            }
        )
        assert response.status_code == 400

        # Names with numbers
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test@Password123",
                "first_name": "Test123",
                "last_name": "User"
            }
        )
        assert response.status_code == 400

    def test_register_email_case_insensitive(self, client: TestClient, test_user: User):
        """Test that email comparison is case-insensitive."""
        # Try to register with same email but different case
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email.upper(),
                "password": "Test@Password123",
                "first_name": "Test",
                "last_name": "User"
            }
        )

        assert response.status_code == 400
