"""
Load testing script for authentication endpoints using Locust.

This script simulates realistic user behavior for load testing the authentication system.

Usage:
    locust -f tests/load/test_load.py --host=http://localhost:8000

    # Or with specific parameters:
    locust -f tests/load/test_load.py --host=http://localhost:8000 --users 100 --spawn-rate 10
"""

from locust import HttpUser, task, between
import random
import string


def random_email():
    """Generate random email for testing."""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{username}@loadtest.com"


def random_password():
    """Generate random valid password."""
    return "LoadTest123!"


class AuthenticationUser(HttpUser):
    """Simulates a user performing authentication operations."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Called when a simulated user starts."""
        self.email = random_email()
        self.password = random_password()
        self.token = None

    @task(1)
    def health_check(self):
        """Test health check endpoint."""
        self.client.get("/api/v1/health")

    @task(3)
    def register_user(self):
        """Test user registration."""
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": random_email(),
                "password": self.password,
                "first_name": "Load",
                "last_name": "Test"
            },
            name="/api/v1/auth/register"
        )

        if response.status_code == 201:
            # Registration successful
            pass
        elif response.status_code == 400:
            # Email already exists (expected in load test)
            pass

    @task(5)
    def login_user(self):
        """Test user login."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": self.email,
                "password": self.password
            },
            name="/api/v1/auth/login"
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")

    @task(2)
    def get_current_user(self):
        """Test getting current user profile."""
        if self.token:
            self.client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {self.token}"},
                name="/api/v1/auth/me"
            )

    @task(1)
    def forgot_password(self):
        """Test forgot password endpoint."""
        self.client.post(
            "/api/v1/auth/forgot-password",
            json={"email": self.email},
            name="/api/v1/auth/forgot-password"
        )


class RegistrationLoadTest(HttpUser):
    """Focused load test for registration endpoint."""

    wait_time = between(0.5, 2)

    @task
    def register(self):
        """Continuously test registration."""
        self.client.post(
            "/api/v1/auth/register",
            json={
                "email": random_email(),
                "password": random_password(),
                "first_name": "Load",
                "last_name": "Test"
            }
        )


class LoginLoadTest(HttpUser):
    """Focused load test for login endpoint."""

    wait_time = between(0.5, 2)

    def on_start(self):
        """Register a user for login testing."""
        self.email = random_email()
        self.password = random_password()

        self.client.post(
            "/api/v1/auth/register",
            json={
                "email": self.email,
                "password": self.password,
                "first_name": "Load",
                "last_name": "Test"
            }
        )

    @task
    def login(self):
        """Continuously test login."""
        self.client.post(
            "/api/v1/auth/login",
            json={
                "email": self.email,
                "password": self.password
            }
        )
