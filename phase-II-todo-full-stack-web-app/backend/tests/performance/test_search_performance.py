"""
Performance tests for search functionality.
"""
import pytest
import time
from fastapi.testclient import TestClient
from sqlmodel import Session
from models import Task, User


class TestSearchPerformance:
    """Test search performance with large datasets."""

    @pytest.fixture
    def large_dataset(self, session: Session, test_user: User):
        """Create 1000 tasks for performance testing."""
        tasks = [
            Task(
                title=f"Task {i} with keywords python javascript",
                description=f"Description {i} about programming and testing",
                user_id=test_user.id,
                priority=["low", "medium", "high"][i % 3],
                status=["todo", "in_progress", "done"][i % 3]
            )
            for i in range(1000)
        ]
        session.add_all(tasks)
        session.commit()
        return tasks

    def test_search_response_time(self, client: TestClient, test_user: User, auth_headers: dict, large_dataset):
        """Test that search completes within 1 second."""
        start = time.time()

        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"search": "python"},
            headers=auth_headers
        )

        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 1.0  # Should complete in < 1 second

    def test_filter_response_time(self, client: TestClient, test_user: User, auth_headers: dict, large_dataset):
        """Test that filtering completes quickly."""
        start = time.time()

        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"status": "done", "priority": "high"},
            headers=auth_headers
        )

        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 0.5  # Should complete in < 500ms

    def test_pagination_performance(self, client: TestClient, test_user: User, auth_headers: dict, large_dataset):
        """Test pagination performance with large dataset."""
        start = time.time()

        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"page": 10, "limit": 20},
            headers=auth_headers
        )

        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 0.5

    def test_combined_filters_performance(self, client: TestClient, test_user: User, auth_headers: dict, large_dataset):
        """Test performance with multiple filters combined."""
        start = time.time()

        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={
                "search": "python",
                "status": "done",
                "priority": "high",
                "sort": "created_at",
                "order": "desc"
            },
            headers=auth_headers
        )

        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 1.0
