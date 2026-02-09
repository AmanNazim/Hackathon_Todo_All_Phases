"""
Load testing script for analytics endpoints using Locust.

This script simulates realistic user behavior for load testing the analytics system.

Usage:
    locust -f tests/load/test_analytics_load.py --host=http://localhost:8000

    # Or with specific parameters:
    locust -f tests/load/test_analytics_load.py --host=http://localhost:8000 --users 200 --spawn-rate 20
"""

from locust import HttpUser, task, between
import random
from datetime import datetime, timedelta


class AnalyticsUser(HttpUser):
    """Simulates a user accessing analytics endpoints."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Called when a simulated user starts."""
        # Login to get token
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test@Password123"
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.user_id = None
            self.headers = {}

    @task(5)
    def get_overview(self):
        """Test analytics overview endpoint (most common)."""
        if self.user_id:
            self.client.get(
                f"/api/v1/users/{self.user_id}/analytics/overview",
                headers=self.headers,
                name="/api/v1/users/{user_id}/analytics/overview"
            )

    @task(3)
    def get_trends(self):
        """Test trends endpoint with various periods."""
        if self.user_id:
            period = random.choice(["daily", "weekly", "monthly"])
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            self.client.get(
                f"/api/v1/users/{self.user_id}/analytics/trends",
                params={
                    "period": period,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                headers=self.headers,
                name="/api/v1/users/{user_id}/analytics/trends"
            )

    @task(2)
    def get_completion_rate(self):
        """Test completion rate endpoint."""
        if self.user_id:
            self.client.get(
                f"/api/v1/users/{self.user_id}/analytics/completion-rate",
                headers=self.headers,
                name="/api/v1/users/{user_id}/analytics/completion-rate"
            )

    @task(2)
    def get_priority_distribution(self):
        """Test priority distribution endpoint."""
        if self.user_id:
            self.client.get(
                f"/api/v1/users/{self.user_id}/analytics/priority-distribution",
                headers=self.headers,
                name="/api/v1/users/{user_id}/analytics/priority-distribution"
            )

    @task(2)
    def get_due_date_adherence(self):
        """Test due date adherence endpoint."""
        if self.user_id:
            period = random.choice(["30days", "90days", "year"])
            self.client.get(
                f"/api/v1/users/{self.user_id}/analytics/due-date-adherence",
                params={"period": period},
                headers=self.headers,
                name="/api/v1/users/{user_id}/analytics/due-date-adherence"
            )

    @task(1)
    def get_productivity_score(self):
        """Test productivity score endpoint."""
        if self.user_id:
            self.client.get(
                f"/api/v1/users/{self.user_id}/analytics/productivity-score",
                headers=self.headers,
                name="/api/v1/users/{user_id}/analytics/productivity-score"
            )

    @task(1)
    def export_csv(self):
        """Test CSV export endpoint."""
        if self.user_id:
            self.client.get(
                f"/api/v1/users/{self.user_id}/analytics/export",
                params={"format": "csv"},
                headers=self.headers,
                name="/api/v1/users/{user_id}/analytics/export?format=csv"
            )

    @task(1)
    def export_json(self):
        """Test JSON export endpoint."""
        if self.user_id:
            self.client.get(
                f"/api/v1/users/{self.user_id}/analytics/export",
                params={"format": "json"},
                headers=self.headers,
                name="/api/v1/users/{user_id}/analytics/export?format=json"
            )


class OverviewLoadTest(HttpUser):
    """Focused load test for overview endpoint."""

    wait_time = between(0.5, 2)

    def on_start(self):
        """Login and get token."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test@Password123"
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            self.headers = {"Authorization": f"Bearer {self.token}"}

    @task
    def get_overview(self):
        """Continuously test overview endpoint."""
        if hasattr(self, 'user_id') and self.user_id:
            self.client.get(
                f"/api/v1/users/{self.user_id}/analytics/overview",
                headers=self.headers
            )


class TrendsLoadTest(HttpUser):
    """Focused load test for trends endpoint."""

    wait_time = between(0.5, 2)

    def on_start(self):
        """Login and get token."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test@Password123"
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            self.headers = {"Authorization": f"Bearer {self.token}"}

    @task
    def get_trends(self):
        """Continuously test trends endpoint."""
        if hasattr(self, 'user_id') and self.user_id:
            period = random.choice(["daily", "weekly", "monthly"])
            end_date = datetime.now()
            start_date = end_date - timedelta(days=random.choice([7, 30, 90]))

            self.client.get(
                f"/api/v1/users/{self.user_id}/analytics/trends",
                params={
                    "period": period,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                headers=self.headers
            )


class ExportLoadTest(HttpUser):
    """Focused load test for export endpoints."""

    wait_time = between(1, 3)

    def on_start(self):
        """Login and get token."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "Test@Password123"
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(2)
    def export_csv(self):
        """Test CSV export."""
        if hasattr(self, 'user_id') and self.user_id:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=random.choice([30, 90, 365]))

            self.client.get(
                f"/api/v1/users/{self.user_id}/analytics/export",
                params={
                    "format": "csv",
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                headers=self.headers
            )

    @task(1)
    def export_json(self):
        """Test JSON export."""
        if hasattr(self, 'user_id') and self.user_id:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=random.choice([30, 90, 365]))

            self.client.get(
                f"/api/v1/users/{self.user_id}/analytics/export",
                params={
                    "format": "json",
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                headers=self.headers
            )
