"""
Load tests for large datasets.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from models import Task, TaskTag, User
from datetime import datetime, timedelta
import random


class TestLargeDatasets:
    """Test system behavior with large datasets."""

    @pytest.fixture
    def large_user_dataset(self, session: Session, test_user: User):
        """Create 10,000 tasks for a single user."""
        print("Creating 10,000 tasks...")

        tasks = []
        for i in range(10000):
            task = Task(
                title=f"Task {i}",
                description=f"Description for task {i}",
                user_id=test_user.id,
                priority=random.choice(["low", "medium", "high", "urgent"]),
                status=random.choice(["todo", "in_progress", "review", "done"]),
                due_date=datetime.utcnow() + timedelta(days=random.randint(1, 30)) if i % 2 == 0 else None
            )
            tasks.append(task)

        session.add_all(tasks)
        session.commit()
        print("✓ Dataset created")
        return tasks

    def test_list_with_large_dataset(self, client: TestClient, test_user: User, auth_headers: dict, large_user_dataset):
        """Test listing tasks with 10,000+ tasks."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"page": 1, "limit": 50},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 10000
        assert len(data["tasks"]) == 50

    def test_search_with_large_dataset(self, client: TestClient, test_user: User, auth_headers: dict, large_user_dataset):
        """Test search performance with large dataset."""
        import time

        start = time.time()
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"search": "Task 1", "limit": 50},
            headers=auth_headers
        )
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 2.0  # Should complete within 2 seconds

    def test_filter_with_large_dataset(self, client: TestClient, test_user: User, auth_headers: dict, large_user_dataset):
        """Test filtering with large dataset."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"status": "done", "priority": "high", "limit": 100},
            headers=auth_headers
        )

        assert response.status_code == 200
        results = response.json()["tasks"]
        assert all(t["status"] == "done" and t["priority"] == "high" for t in results)

    def test_batch_operation_with_many_tasks(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test batch operations with many tasks."""
        # Create 100 tasks
        tasks = [Task(title=f"Batch {i}", user_id=test_user.id) for i in range(100)]
        session.add_all(tasks)
        session.commit()
        task_ids = [str(t.id) for t in tasks]

        # Batch update
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks/batch",
            json={
                "task_ids": task_ids,
                "operation": "update_status",
                "status": "done"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["updated"] == 100
