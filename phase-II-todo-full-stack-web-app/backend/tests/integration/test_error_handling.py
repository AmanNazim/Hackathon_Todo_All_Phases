"""
Integration tests for error handling and edge cases.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from models import Task, User


class TestErrorHandling:
    """Test error handling for various scenarios."""

    def test_create_task_without_title(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test creating task without required title."""
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks",
            json={"description": "No title"},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_get_nonexistent_task(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test getting a task that doesn't exist."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_update_with_invalid_status(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test updating task with invalid status."""
        task = Task(title="Test", user_id=test_user.id)
        session.add(task)
        session.commit()

        response = client.put(
            f"/api/v1/users/{test_user.id}/tasks/{task.id}",
            json={"status": "invalid_status"},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_unauthorized_access(self, client: TestClient, test_user: User):
        """Test accessing endpoints without authentication."""
        response = client.get(f"/api/v1/users/{test_user.id}/tasks")
        assert response.status_code == 401

    def test_invalid_pagination_params(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test invalid pagination parameters."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"page": -1, "limit": 0},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_search_with_empty_query(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test search with empty query string."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"search": ""},
            headers=auth_headers
        )
        assert response.status_code == 200  # Should return all tasks

    def test_batch_operation_with_invalid_ids(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test batch operation with invalid task IDs."""
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks/batch",
            json={
                "task_ids": ["invalid", "also-invalid"],
                "operation": "delete"
            },
            headers=auth_headers
        )
        assert response.status_code in [400, 422]

    def test_database_constraint_violation(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test handling of database constraint violations."""
        # Create task
        task = Task(title="Test", user_id=test_user.id)
        session.add(task)
        session.commit()

        # Try to add duplicate tag (if unique constraint exists)
        from models import TaskTag
        tag1 = TaskTag(task_id=task.id, tag="duplicate")
        session.add(tag1)
        session.commit()

        # Try to add same tag again
        tag2 = TaskTag(task_id=task.id, tag="duplicate")
        session.add(tag2)

        with pytest.raises(Exception):  # Should raise integrity error
            session.commit()
