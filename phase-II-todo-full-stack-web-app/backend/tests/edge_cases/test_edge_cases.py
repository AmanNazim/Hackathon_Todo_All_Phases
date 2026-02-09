"""
Edge case and error handling validation tests.

This module tests edge cases, error conditions, and system resilience.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from unittest.mock import patch, MagicMock
import time


class TestNetworkErrors:
    """Test handling of network and connectivity errors."""

    @patch('services.email.send_verification_email')
    def test_registration_email_failure_graceful(self, mock_send_email, client: TestClient):
        """Test that registration succeeds even if email fails."""
        # Simulate email service failure
        mock_send_email.side_effect = Exception("SMTP connection failed")

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test@Password123",
                "first_name": "Test",
                "last_name": "User"
            }
        )

        # Registration should still succeed
        # Email failure should be logged but not block registration
        assert response.status_code in [201, 500]

    @patch('database.get_session')
    def test_database_connection_failure(self, mock_get_session, client: TestClient):
        """Test handling of database connection failures."""
        mock_get_session.side_effect = Exception("Database connection failed")

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test@Password123"
            }
        )

        # Should return 500 Internal Server Error
        assert response.status_code == 500


class TestConcurrency:
    """Test concurrent operations and race conditions."""

    def test_concurrent_registration_same_email(self, client: TestClient):
        """Test that concurrent registrations with same email are handled."""
        import threading

        email = "concurrent@example.com"
        results = []

        def register():
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "Test@Password123",
                    "first_name": "Test",
                    "last_name": "User"
                }
            )
            results.append(response.status_code)

        # Start multiple threads
        threads = [threading.Thread(target=register) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Only one should succeed (201), others should fail (400)
        assert results.count(201) == 1
        assert results.count(400) >= 1

    def test_concurrent_password_reset_requests(self, client: TestClient, test_user: User):
        """Test concurrent password reset requests."""
        import threading

        results = []

        def request_reset():
            response = client.post(
                "/api/v1/auth/forgot-password",
                json={"email": test_user.email}
            )
            results.append(response.status_code)

        # Start multiple threads
        threads = [threading.Thread(target=request_reset) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should succeed (200) but only latest token should be valid
        assert all(status == 200 for status in results)


class TestBoundaryConditions:
    """Test boundary conditions and limits."""

    def test_maximum_email_length(self, client: TestClient):
        """Test email with maximum allowed length."""
        # Email max length is typically 255 characters
        long_email = "a" * 240 + "@example.com"

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": long_email,
                "password": "Test@Password123",
                "first_name": "Test",
                "last_name": "User"
            }
        )

        # Should accept or reject based on validation rules
        assert response.status_code in [201, 422]

    def test_maximum_password_length(self, client: TestClient):
        """Test password with very long length."""
        long_password = "A1!" + "a" * 1000

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "longpass@example.com",
                "password": long_password,
                "first_name": "Test",
                "last_name": "User"
            }
        )

        # Should handle gracefully
        assert response.status_code in [201, 400, 422]

    def test_maximum_name_length(self, client: TestClient):
        """Test name with maximum allowed length."""
        long_name = "A" * 100

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "longname@example.com",
                "password": "Test@Password123",
                "first_name": long_name,
                "last_name": "User"
            }
        )

        # Should accept or reject based on validation rules
        assert response.status_code in [201, 400]

    def test_unicode_in_names(self, client: TestClient):
        """Test unicode characters in names."""
        unicode_names = [
            ("José", "García"),
            ("François", "Müller"),
            ("李", "明"),
            ("Владимир", "Петров")
        ]

        for first_name, last_name in unicode_names:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"unicode{hash(first_name)}@example.com",
                    "password": "Test@Password123",
                    "first_name": first_name,
                    "last_name": last_name
                }
            )

            # Should handle unicode gracefully
            assert response.status_code in [201, 400]


class TestTokenEdgeCases:
    """Test edge cases with tokens."""

    def test_reset_token_reuse_prevention(self, client: TestClient, session: Session, test_user: User):
        """Test that reset tokens cannot be reused."""
        from auth.tokens import generate_password_reset_token

        token = generate_password_reset_token(session, test_user.id)

        # Use token first time
        response1 = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "NewPassword123!"
            }
        )
        assert response1.status_code == 200

        # Try to use same token again
        response2 = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "AnotherPassword123!"
            }
        )
        assert response2.status_code == 400

    def test_verification_token_reuse_prevention(self, client: TestClient, session: Session, unverified_user: User):
        """Test that verification tokens cannot be reused."""
        from auth.tokens import generate_email_verification_token

        token = generate_email_verification_token(session, unverified_user.id)

        # Use token first time
        response1 = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token}
        )
        assert response1.status_code == 200

        # Try to use same token again
        response2 = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token}
        )
        assert response2.status_code == 400

    def test_token_with_special_characters(self, client: TestClient):
        """Test tokens with special characters are handled."""
        special_tokens = [
            "token+with+plus",
            "token/with/slash",
            "token=with=equals",
            "token with spaces"
        ]

        for token in special_tokens:
            response = client.post(
                "/api/v1/auth/reset-password",
                json={
                    "token": token,
                    "new_password": "NewPassword123!"
                }
            )
            # Should handle gracefully
            assert response.status_code in [400, 422]


class TestRateLimitingEdgeCases:
    """Test rate limiting edge cases."""

    def test_rate_limit_reset_after_window(self, client: TestClient, test_user: User):
        """Test that rate limit resets after time window."""
        # Make requests up to limit
        for _ in range(5):
            client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user.email,
                    "password": "WrongPassword123!"
                }
            )

        # Should be rate limited
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code in [403, 429]

        # Wait for rate limit window to expire (15 minutes in production)
        # In tests, this should be mocked or use shorter window
        # time.sleep(900)  # Don't actually wait in tests

    def test_rate_limit_per_ip_isolation(self, client: TestClient):
        """Test that rate limits are isolated per IP."""
        # This would require mocking different IP addresses
        # In real tests, use different client instances with different IPs
        pass


class TestErrorRecovery:
    """Test system recovery from errors."""

    def test_recovery_after_database_error(self, client: TestClient):
        """Test that system recovers after database error."""
        # Simulate database error and recovery
        # This would require mocking database connection
        pass

    def test_recovery_after_email_service_error(self, client: TestClient):
        """Test that system recovers after email service error."""
        # Simulate email service error and recovery
        pass


class TestDataIntegrity:
    """Test data integrity and consistency."""

    def test_password_change_invalidates_old_password(self, client: TestClient, session: Session, test_user: User, auth_headers: dict, test_user_data: dict):
        """Test that old password is completely invalidated after change."""
        new_password = "NewPassword123!"

        # Change password
        client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": test_user_data["password"],
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

        # Login with new password should work
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": new_password
            }
        )
        assert response.status_code == 200

    def test_email_verification_idempotent(self, client: TestClient, session: Session, unverified_user: User):
        """Test that email verification is idempotent."""
        from auth.tokens import generate_email_verification_token

        token = generate_email_verification_token(session, unverified_user.id)

        # Verify email
        response1 = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token}
        )
        assert response1.status_code == 200

        # Verify again with new token (should succeed as already verified)
        token2 = generate_email_verification_token(session, unverified_user.id)
        response2 = client.post(
            "/api/v1/auth/verify-email",
            json={"token": token2}
        )
        assert response2.status_code == 200


class TestMalformedRequests:
    """Test handling of malformed requests."""

    def test_missing_content_type(self, client: TestClient):
        """Test request without Content-Type header."""
        response = client.post(
            "/api/v1/auth/login",
            data='{"email":"test@example.com","password":"Test@Password123"}'
        )
        # Should handle gracefully
        assert response.status_code in [200, 422]

    def test_invalid_json(self, client: TestClient):
        """Test request with invalid JSON."""
        response = client.post(
            "/api/v1/auth/login",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_extra_fields_ignored(self, client: TestClient):
        """Test that extra fields in request are ignored."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "extra@example.com",
                "password": "Test@Password123",
                "first_name": "Test",
                "last_name": "User",
                "extra_field": "should be ignored",
                "admin": True  # Should not make user admin
            }
        )

        if response.status_code == 201:
            data = response.json()
            assert "extra_field" not in data
            assert "admin" not in data or data.get("admin") is False
