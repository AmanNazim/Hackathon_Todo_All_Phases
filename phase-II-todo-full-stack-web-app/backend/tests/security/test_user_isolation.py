"""
Security tests for user isolation.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from models import Task, User
from auth import get_password_hash


class TestUserIsolation:
    """Test that users can only access their own tasks."""

    def test_user_cannot_view_other_user_tasks(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test that users cannot view tasks from other users."""
        # Create another user
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("Test@Password123"),
            first_name="Other",
            last_name="User"
        )
        session.add(other_user)
        session.commit()
        session.refresh(other_user)

        # Create task for other user
        other_task = Task(title="Other's Task", user_id=other_user.id)
        session.add(other_task)
        session.commit()

        # Try to access other user's task
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks/{other_task.id}",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_user_cannot_update_other_user_tasks(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test that users cannot update tasks from other users."""
        other_user = User(
            email="other2@example.com",
            password_hash=get_password_hash("Test@Password123"),
            first_name="Other",
            last_name="User"
        )
        session.add(other_user)
        session.commit()

        other_task = Task(title="Other's Task", user_id=other_user.id)
        session.add(other_task)
        session.commit()

        # Try to update other user's task
        response = client.put(
            f"/api/v1/users/{test_user.id}/tasks/{other_task.id}",
            json={"title": "Hacked"},
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_user_cannot_delete_other_user_tasks(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test that users cannot delete tasks from other users."""
        other_user = User(
            email="other3@example.com",
            password_hash=get_password_hash("Test@Password123"),
            first_name="Other",
            last_name="User"
        )
        session.add(other_user)
        session.commit()

        other_task = Task(title="Other's Task", user_id=other_user.id)
        session.add(other_task)
        session.commit()

        # Try to delete other user's task
        response = client.delete(
            f"/api/v1/users/{test_user.id}/tasks/{other_task.id}",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_task_list_only_shows_own_tasks(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test that task list only shows user's own tasks."""
        other_user = User(
            email="other4@example.com",
            password_hash=get_password_hash("Test@Password123"),
            first_name="Other",
            last_name="User"
        )
        session.add(other_user)
        session.commit()

        # Create tasks for both users
        my_task = Task(title="My Task", user_id=test_user.id)
        other_task = Task(title="Other's Task", user_id=other_user.id)
        session.add_all([my_task, other_task])
        session.commit()

        # Get task list
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            headers=auth_headers
        )
        assert response.status_code == 200
        tasks = response.json()["tasks"]
        assert len(tasks) == 1
        assert tasks[0]["title"] == "My Task"
