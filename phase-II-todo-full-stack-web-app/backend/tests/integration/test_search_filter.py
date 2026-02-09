"""
Integration tests for search and filtering functionality.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime, timedelta
from models import Task, User


class TestFullTextSearch:
    """Test full-text search functionality."""

    def test_search_by_title(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test searching tasks by title."""
        # Create tasks with different titles
        tasks = [
            Task(title="Python programming", user_id=test_user.id),
            Task(title="JavaScript development", user_id=test_user.id),
            Task(title="Python testing", user_id=test_user.id)
        ]
        session.add_all(tasks)
        session.commit()

        # Search for "Python"
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"search": "Python"},
            headers=auth_headers
        )
        assert response.status_code == 200
        results = response.json()["tasks"]
        assert len(results) == 2

    def test_search_by_description(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test searching tasks by description."""
        task = Task(
            title="Task 1",
            description="This is about machine learning algorithms",
            user_id=test_user.id
        )
        session.add(task)
        session.commit()

        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"search": "machine learning"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert len(response.json()["tasks"]) >= 1


class TestFiltering:
    """Test task filtering functionality."""

    def test_filter_by_status(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test filtering tasks by status."""
        tasks = [
            Task(title="Todo 1", status="todo", user_id=test_user.id),
            Task(title="Done 1", status="done", user_id=test_user.id),
            Task(title="Todo 2", status="todo", user_id=test_user.id)
        ]
        session.add_all(tasks)
        session.commit()

        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"status": "todo"},
            headers=auth_headers
        )
        assert response.status_code == 200
        results = response.json()["tasks"]
        assert len(results) == 2
        assert all(t["status"] == "todo" for t in results)

    def test_filter_by_priority(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test filtering tasks by priority."""
        tasks = [
            Task(title="High 1", priority="high", user_id=test_user.id),
            Task(title="Low 1", priority="low", user_id=test_user.id),
            Task(title="High 2", priority="high", user_id=test_user.id)
        ]
        session.add_all(tasks)
        session.commit()

        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"priority": "high"},
            headers=auth_headers
        )
        assert response.status_code == 200
        results = response.json()["tasks"]
        assert len(results) == 2
        assert all(t["priority"] == "high" for t in results)

    def test_filter_by_date_range(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test filtering tasks by due date range."""
        now = datetime.utcnow()
        tasks = [
            Task(title="Soon", due_date=now + timedelta(days=1), user_id=test_user.id),
            Task(title="Later", due_date=now + timedelta(days=10), user_id=test_user.id),
            Task(title="Much later", due_date=now + timedelta(days=30), user_id=test_user.id)
        ]
        session.add_all(tasks)
        session.commit()

        # Filter for tasks due within 7 days
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={
                "due_after": now.isoformat(),
                "due_before": (now + timedelta(days=7)).isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        results = response.json()["tasks"]
        assert len(results) == 2


class TestSorting:
    """Test task sorting functionality."""

    def test_sort_by_due_date(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test sorting tasks by due date."""
        now = datetime.utcnow()
        tasks = [
            Task(title="Task 3", due_date=now + timedelta(days=3), user_id=test_user.id),
            Task(title="Task 1", due_date=now + timedelta(days=1), user_id=test_user.id),
            Task(title="Task 2", due_date=now + timedelta(days=2), user_id=test_user.id)
        ]
        session.add_all(tasks)
        session.commit()

        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"sort": "due_date", "order": "asc"},
            headers=auth_headers
        )
        assert response.status_code == 200
        results = response.json()["tasks"]
        assert results[0]["title"] == "Task 1"
        assert results[1]["title"] == "Task 2"
        assert results[2]["title"] == "Task 3"

    def test_sort_by_priority(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test sorting tasks by priority."""
        tasks = [
            Task(title="Low", priority="low", user_id=test_user.id),
            Task(title="High", priority="high", user_id=test_user.id),
            Task(title="Medium", priority="medium", user_id=test_user.id)
        ]
        session.add_all(tasks)
        session.commit()

        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"sort": "priority", "order": "desc"},
            headers=auth_headers
        )
        assert response.status_code == 200
        # Priority order: urgent > high > medium > low
        results = response.json()["tasks"]
        assert results[0]["priority"] == "high"


class TestPagination:
    """Test pagination functionality."""

    def test_pagination_basic(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test basic pagination."""
        # Create 25 tasks
        tasks = [Task(title=f"Task {i}", user_id=test_user.id) for i in range(25)]
        session.add_all(tasks)
        session.commit()

        # Get first page (10 items)
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"page": 1, "limit": 10},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 10
        assert data["total"] == 25
        assert data["page"] == 1

    def test_pagination_last_page(self, client: TestClient, session: Session, test_user: User, auth_headers: dict):
        """Test last page of pagination."""
        tasks = [Task(title=f"Task {i}", user_id=test_user.id) for i in range(25)]
        session.add_all(tasks)
        session.commit()

        # Get last page
        response = client.get(
            f"/api/v1/users/{test_user.id}/tasks",
            params={"page": 3, "limit": 10},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 5  # Remaining items
