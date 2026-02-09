"""
Integration tests for batch operations.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from models import Task, User


class TestBatchStatusUpdate:
    """Test batch status update operations."""

    def test_batch_update_status(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test updating status for multiple tasks."""
        # Create tasks
        tasks = [
            Task(title=f"Task {i}", status="todo", user_id=test_user.id)
            for i in range(5)
        ]
        session.add_all(tasks)
        session.commit()
        task_ids = [str(task.id) for task in tasks]

        # Batch update status
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks/batch",
            json={
                "task_ids": task_ids,
                "operation": "update_status",
                "status": "in_progress"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert result["updated"] == 5

        # Verify all tasks updated
        for task_id in task_ids:
            response = client.get(
                f"/api/v1/users/{test_user.id}/tasks/{task_id}",
                headers=auth_headers
            )
            assert response.json()["status"] == "in_progress"


class TestBatchDeletion:
    """Test batch deletion operations."""

    def test_batch_delete_tasks(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test deleting multiple tasks."""
        tasks = [
            Task(title=f"Task {i}", user_id=test_user.id)
            for i in range(3)
        ]
        session.add_all(tasks)
        session.commit()
        task_ids = [str(task.id) for task in tasks]

        # Batch delete
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks/batch",
            json={
                "task_ids": task_ids,
                "operation": "delete"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["deleted"] == 3

        # Verify tasks are soft deleted
        for task_id in task_ids:
            response = client.get(
                f"/api/v1/users/{test_user.id}/tasks/{task_id}",
                headers=auth_headers
            )
            assert response.status_code == 404


class TestBatchTagOperations:
    """Test batch tag operations."""

    def test_batch_add_tags(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test adding tags to multiple tasks."""
        tasks = [
            Task(title=f"Task {i}", user_id=test_user.id)
            for i in range(3)
        ]
        session.add_all(tasks)
        session.commit()
        task_ids = [str(task.id) for task in tasks]

        # Batch add tags
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks/batch",
            json={
                "task_ids": task_ids,
                "operation": "add_tags",
                "tags": ["urgent", "work"]
            },
            headers=auth_headers
        )
        assert response.status_code == 200

        # Verify tags added
        for task_id in task_ids:
            response = client.get(
                f"/api/v1/users/{test_user.id}/tasks/{task_id}",
                headers=auth_headers
            )
            tags = response.json()["tags"]
            assert "urgent" in tags
            assert "work" in tags


class TestBatchErrorHandling:
    """Test error handling in batch operations."""

    def test_partial_failure_handling(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test handling of partial failures in batch operations."""
        # Create valid tasks
        tasks = [
            Task(title=f"Task {i}", user_id=test_user.id)
            for i in range(2)
        ]
        session.add_all(tasks)
        session.commit()
        valid_ids = [str(task.id) for task in tasks]

        # Include invalid ID
        task_ids = valid_ids + ["invalid-uuid"]

        # Batch operation with partial failure
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks/batch",
            json={
                "task_ids": task_ids,
                "operation": "update_status",
                "status": "done"
            },
            headers=auth_headers
        )

        # Should return partial success
        assert response.status_code == 200
        result = response.json()
        assert result["updated"] == 2
        assert result["failed"] == 1

    def test_empty_batch_operation(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test batch operation with empty task list."""
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks/batch",
            json={
                "task_ids": [],
                "operation": "update_status",
                "status": "done"
            },
            headers=auth_headers
        )
        assert response.status_code == 400
