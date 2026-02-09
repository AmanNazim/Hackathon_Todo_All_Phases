"""
Integration tests for analytics endpoints.

Tests overview, trends, adherence, productivity score, and export endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime, timedelta
from models import Task, User


class TestOverviewEndpoint:
    """Test suite for analytics overview endpoint."""

    def test_overview_success(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test successful overview retrieval."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/overview",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "total" in data
        assert "completed" in data
        assert "pending" in data
        assert "completion_rate" in data
        assert "overdue" in data
        assert "by_priority" in data
        assert "by_status" in data

    def test_overview_with_tasks(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test overview with actual task data."""
        # Create test tasks
        for i in range(10):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done" if i < 7 else "todo",
                priority="high" if i < 3 else "medium"
            )
            session.add(task)
        session.commit()

        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/overview",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 10
        assert data["completed"] == 7
        assert data["pending"] == 3
        assert data["completion_rate"] == 70.0

    def test_overview_requires_authentication(self, client: TestClient, test_user: User):
        """Test that overview requires authentication."""
        response = client.get(f"/api/v1/users/{test_user.id}/analytics/overview")

        assert response.status_code == 401

    def test_overview_user_isolation(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test that users can only access their own analytics."""
        from uuid import uuid4

        # Try to access another user's analytics
        other_user_id = uuid4()
        response = client.get(
            f"/api/v1/users/{other_user_id}/analytics/overview",
            headers=auth_headers
        )

        assert response.status_code == 403


class TestTrendsEndpoint:
    """Test suite for trends endpoint."""

    def test_trends_daily(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test daily trends retrieval."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/trends",
            params={
                "period": "daily",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

    def test_trends_weekly(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test weekly trends retrieval."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=28)

        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/trends",
            params={
                "period": "weekly",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

    def test_trends_monthly(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test monthly trends retrieval."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/trends",
            params={
                "period": "monthly",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

    def test_trends_invalid_period(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test trends with invalid period."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/trends",
            params={"period": "invalid"},
            headers=auth_headers
        )

        assert response.status_code == 400

    def test_trends_missing_dates(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test trends without date parameters."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/trends",
            params={"period": "daily"},
            headers=auth_headers
        )

        # Should use default date range or return error
        assert response.status_code in [200, 400]


class TestCompletionRateEndpoint:
    """Test suite for completion rate endpoint."""

    def test_completion_rate_success(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test successful completion rate retrieval."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/completion-rate",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "rate" in data
        assert isinstance(data["rate"], (int, float))
        assert 0 <= data["rate"] <= 100


class TestPriorityDistributionEndpoint:
    """Test suite for priority distribution endpoint."""

    def test_priority_distribution_success(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test successful priority distribution retrieval."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/priority-distribution",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, dict)
        # Should have priority levels
        assert all(key in ["high", "medium", "low"] for key in data.keys() if key != "total")


class TestDueDateAdherenceEndpoint:
    """Test suite for due date adherence endpoint."""

    def test_adherence_30_days(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test adherence for 30 days period."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/due-date-adherence",
            params={"period": "30days"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "adherence_rate" in data
        assert isinstance(data["adherence_rate"], (int, float))

    def test_adherence_90_days(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test adherence for 90 days period."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/due-date-adherence",
            params={"period": "90days"},
            headers=auth_headers
        )

        assert response.status_code == 200

    def test_adherence_year(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test adherence for year period."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/due-date-adherence",
            params={"period": "year"},
            headers=auth_headers
        )

        assert response.status_code == 200


class TestProductivityScoreEndpoint:
    """Test suite for productivity score endpoint."""

    def test_productivity_score_success(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test successful productivity score retrieval."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/productivity-score",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "score" in data
        assert isinstance(data["score"], (int, float))
        assert 0 <= data["score"] <= 100

    def test_productivity_score_breakdown(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test productivity score includes breakdown."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/productivity-score",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should include component scores
        assert "completion_rate" in data or "components" in data


class TestExportEndpoints:
    """Test suite for export endpoints."""

    def test_export_csv(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test CSV export."""
        # Create some tasks
        for i in range(5):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done" if i < 3 else "todo"
            )
            session.add(task)
        session.commit()

        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/export",
            params={"format": "csv"},
            headers=auth_headers
        )

        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    def test_export_json(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test JSON export."""
        # Create some tasks
        for i in range(5):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done"
            )
            session.add(task)
        session.commit()

        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/export",
            params={"format": "json"},
            headers=auth_headers
        )

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

        data = response.json()
        assert isinstance(data, list)

    def test_export_with_date_range(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test export with date range filtering."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/export",
            params={
                "format": "csv",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            headers=auth_headers
        )

        assert response.status_code == 200

    def test_export_invalid_format(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test export with invalid format."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/export",
            params={"format": "xml"},
            headers=auth_headers
        )

        assert response.status_code == 400


class TestAnalyticsErrorHandling:
    """Test suite for error handling in analytics endpoints."""

    def test_invalid_user_id(self, client: TestClient, auth_headers: dict):
        """Test analytics with invalid user ID."""
        response = client.get(
            "/api/v1/users/invalid-uuid/analytics/overview",
            headers=auth_headers
        )

        assert response.status_code in [400, 422]

    def test_invalid_date_format(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test trends with invalid date format."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/trends",
            params={
                "period": "daily",
                "start_date": "invalid-date",
                "end_date": "2024-01-01"
            },
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_end_date_before_start_date(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test trends with end date before start date."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/trends",
            params={
                "period": "daily",
                "start_date": "2024-12-31",
                "end_date": "2024-01-01"
            },
            headers=auth_headers
        )

        assert response.status_code == 400
