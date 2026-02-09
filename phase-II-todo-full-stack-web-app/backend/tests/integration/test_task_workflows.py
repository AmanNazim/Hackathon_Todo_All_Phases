"""
Integration tests for task workflows.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime
from models import Task, TaskTag, User


class TestTaskWorkflow:
    """Test complete task workflow from creation to completion."""

    def test_complete_task_lifecycle(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test full task lifecycle: create -> update -> complete -> delete."""
        # Create task
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks",
            json={
                "title": "Lifecycle Test Task",
                "description": "Testing full lifecycle",
                "priority": "high",
                "status": "todo"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        task_id = response.json()["id"]

        # Update task
        response = client.put(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}",
            json={"status": "in_progress"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

        # Complete task
        response = client.patch(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}/complete",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "done"
        assert response.json()["completed_at"] is not None

        # Delete task
        response = client.delete(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}",
            headers=auth_headers
        )
        assert response.status_code == 204


class TestStatusTransitions:
    """Test status transition workflows."""

    def test_valid_status_progression(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test valid status transitions."""
        # Create task
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks",
            json={"title": "Status Test", "status": "todo"},
            headers=auth_headers
        )
        task_id = response.json()["id"]

        # todo -> in_progress
        response = client.put(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}",
            json={"status": "in_progress"},
            headers=auth_headers
        )
        assert response.status_code == 200

        # in_progress -> review
        response = client.put(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}",
            json={"status": "review"},
            headers=auth_headers
        )
        assert response.status_code == 200

        # review -> done
        response = client.put(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}",
            json={"status": "done"},
            headers=auth_headers
        )
        assert response.status_code == 200


class TestTagManagement:
    """Test tag management workflows."""

    def test_add_and_remove_tags(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test adding and removing tags from a task."""
        # Create task
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks",
            json={"title": "Tag Test Task"},
            headers=auth_headers
        )
        task_id = response.json()["id"]

        # Add tags
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}/tags",
            json={"tags": ["work", "urgent"]},
            headers=auth_headers
        )
        assert response.status_code == 200

        # Get task with tags
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}",
            headers=auth_headers
        )
        assert len(response.json()["tags"]) == 2

        # Remove tag
        response = client.delete(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}/tags",
            json={"tag": "urgent"},
            headers=auth_headers
        )
        assert response.status_code == 200

        # Verify tag removed
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}",
            headers=auth_headers
        )
        tags = response.json()["tags"]
        assert len(tags) == 1
        assert tags[0] == "work"


class TestTaskHistory:
    """Test task history tracking."""

    def test_history_created_on_changes(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test that history entries are created for task changes."""
        # Create task
        response = client.post(
            f"/api/v1/users/{test_user.id}/tasks",
            json={"title": "History Test", "status": "todo"},
            headers=auth_headers
        )
        task_id = response.json()["id"]

        # Update task multiple times
        client.put(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}",
            json={"status": "in_progress"},
            headers=auth_headers
        )
        client.put(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}",
            json={"priority": "high"},
            headers=auth_headers
        )

        # Get history
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks/{task_id}/history",
            headers=auth_headers
        )
        assert response.status_code == 200
        history = response.json()
        assert len(history) >= 2  # At least 2 changes
