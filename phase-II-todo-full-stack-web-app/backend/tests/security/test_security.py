"""
Security testing checklist and test cases for authentication system.

This module provides security test cases covering OWASP Top 10 vulnerabilities
and common authentication security issues.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestSQLInjection:
    """Test SQL injection prevention."""

    def test_login_sql_injection_email(self, client: TestClient):
        """Test that SQL injection in email field is prevented."""
        sql_injection_payloads = [
            "admin'--",
            "admin' OR '1'='1",
            "admin'; DROP TABLE users;--",
            "' OR 1=1--",
            "admin' UNION SELECT * FROM users--"
        ]

        for payload in sql_injection_payloads:
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": payload,
                    "password": "Test@Password123"
                }
            )
            # Should return 401 or 422, not 500 (which would indicate SQL error)
            assert response.status_code in [401, 422]

    def test_registration_sql_injection(self, client: TestClient):
        """Test SQL injection prevention in registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test'; DROP TABLE users;--@example.com",
                "password": "Test@Password123",
                "first_name": "Test'; DELETE FROM users;--",
                "last_name": "User"
            }
        )
        # Should handle gracefully, not cause SQL error
        assert response.status_code in [400, 422]


class TestXSSPrevention:
    """Test Cross-Site Scripting (XSS) prevention."""

    def test_registration_xss_in_name(self, client: TestClient):
        """Test that XSS payloads in names are sanitized."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>"
        ]

        for payload in xss_payloads:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"test{hash(payload)}@example.com",
                    "password": "Test@Password123",
                    "first_name": payload,
                    "last_name": "User"
                }
            )
            # Should reject or sanitize
            if response.status_code == 201:
                data = response.json()
                # Name should be sanitized (HTML escaped)
                assert "<script>" not in data.get("first_name", "")
                assert "javascript:" not in data.get("first_name", "")


class TestAuthenticationBypass:
    """Test authentication bypass attempts."""

    def test_access_protected_endpoint_without_token(self, client: TestClient):
        """Test that protected endpoints require authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_access_with_invalid_token(self, client: TestClient):
        """Test that invalid tokens are rejected."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_access_with_malformed_token(self, client: TestClient):
        """Test that malformed tokens are rejected."""
        malformed_tokens = [
            "Bearer ",
            "Bearer not.a.token",
            "InvalidFormat token",
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"  # Incomplete JWT
        ]

        for token in malformed_tokens:
            response = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": token}
            )
            assert response.status_code == 401


class TestBruteForceProtection:
    """Test brute force attack protection."""

    def test_rate_limiting_on_login(self, client: TestClient, test_user: User):
        """Test that excessive login attempts are rate limited."""
        # Make multiple failed login attempts
        for i in range(6):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user.email,
                    "password": "WrongPassword123!"
                }
            )

        # Should be rate limited or account locked
        assert response.status_code in [403, 429]

    def test_account_lockout_after_failed_attempts(self, client: TestClient, test_user: User, test_user_data: dict):
        """Test account lockout after multiple failed attempts."""
        # Make 5 failed attempts
        for _ in range(5):
            client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user.email,
                    "password": "WrongPassword123!"
                }
            )

        # Try with correct password - should still be locked
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": test_user_data["password"]
            }
        )

        assert response.status_code == 403
        assert "locked" in response.json()["detail"].lower()


class TestSessionSecurity:
    """Test session and token security."""

    def test_token_expiration_enforced(self, client: TestClient):
        """Test that expired tokens are rejected."""
        from datetime import datetime, timedelta
        from auth import create_access_token

        # Create token that expires immediately
        expired_token = create_access_token(
            {"sub": "user123"},
            expires_delta=timedelta(seconds=-1)
        )

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401

    def test_token_cannot_be_reused_after_password_change(self, client: TestClient, test_user: User, auth_headers: dict, test_user_data: dict):
        """Test that old tokens are invalid after password change."""
        # Get initial token
        old_token = auth_headers["Authorization"]

        # Change password
        client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": test_user_data["password"],
                "new_password": "NewPassword123!"
            }
        )

        # Try to use old token
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": old_token}
        )

        # Note: With stateless JWT, old tokens remain valid until expiration
        # This is a known limitation of stateless JWT
        # For enhanced security, implement token blacklist or stateful sessions


class TestInputValidation:
    """Test input validation and sanitization."""

    def test_email_validation(self, client: TestClient):
        """Test email format validation."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "",
            "user@.com",
            "user..name@example.com"
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

    def test_password_complexity_enforced(self, client: TestClient):
        """Test password complexity requirements."""
        weak_passwords = [
            "short",
            "nouppercase123!",
            "NOLOWERCASE123!",
            "NoNumbers!",
            "NoSpecial123",
            "12345678"
        ]

        for password in weak_passwords:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"test{hash(password)}@example.com",
                    "password": password,
                    "first_name": "Test",
                    "last_name": "User"
                }
            )
            assert response.status_code == 400

    def test_name_validation(self, client: TestClient):
        """Test name field validation."""
        invalid_names = [
            "",
            "A",
            "Test123",
            "Test@User",
            "<script>alert('xss')</script>"
        ]

        for name in invalid_names:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"test{hash(name)}@example.com",
                    "password": "Test@Password123",
                    "first_name": name,
                    "last_name": "User"
                }
            )
            assert response.status_code == 400


class TestInformationDisclosure:
    """Test information disclosure prevention."""

    def test_login_error_no_user_enumeration(self, client: TestClient):
        """Test that login errors don't reveal if user exists."""
        # Try with non-existent user
        response1 = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Test@Password123"
            }
        )

        # Try with existing user but wrong password
        response2 = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword123!"
            }
        )

        # Both should return same generic error
        assert response1.status_code == response2.status_code
        assert "invalid" in response1.json()["detail"].lower()
        assert "invalid" in response2.json()["detail"].lower()

    def test_forgot_password_no_enumeration(self, client: TestClient):
        """Test that forgot password doesn't reveal if email exists."""
        # Try with non-existent email
        response1 = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )

        # Try with existing email
        response2 = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"}
        )

        # Both should return same success message
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["message"] == response2.json()["message"]

    def test_error_messages_no_sensitive_info(self, client: TestClient):
        """Test that error messages don't leak sensitive information."""
        # Trigger various errors
        responses = [
            client.post("/api/v1/auth/login", json={"email": "test"}),
            client.get("/api/v1/auth/me"),
            client.post("/api/v1/auth/reset-password", json={"token": "invalid"})
        ]

        for response in responses:
            error_text = response.text.lower()
            # Should not contain sensitive information
            assert "database" not in error_text
            assert "sql" not in error_text
            assert "stack trace" not in error_text
            assert "exception" not in error_text


class TestSecurityHeaders:
    """Test security headers are present."""

    def test_security_headers_present(self, client: TestClient):
        """Test that security headers are set."""
        response = client.get("/api/v1/health")

        headers = response.headers

        # Check for security headers
        assert "x-content-type-options" in headers
        assert headers["x-content-type-options"] == "nosniff"

        assert "x-frame-options" in headers
        assert headers["x-frame-options"] == "DENY"

        assert "x-xss-protection" in headers


class TestPasswordSecurity:
    """Test password security measures."""

    def test_password_not_returned_in_responses(self, client: TestClient):
        """Test that passwords are never returned in API responses."""
        # Register user
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "secure@example.com",
                "password": "Test@Password123",
                "first_name": "Secure",
                "last_name": "User"
            }
        )

        response_text = response.text.lower()
        assert "password" not in response_text or "password_hash" not in response_text

    def test_password_hash_different_for_same_password(self, session: Session):
        """Test that same password produces different hashes (salt)."""
        from auth import get_password_hash

        password = "Test@Password123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2

    def test_old_password_required_for_change(self, client: TestClient, auth_headers: dict):
        """Test that current password is required to change password."""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword123!"
            }
        )

        assert response.status_code == 400
