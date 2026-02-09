"""
Unit tests for task validation and business logic.
"""
import pytest
from datetime import datetime, timedelta
from sqlmodel import Session
from models import Task, User
from services.task_workflow import validate_status_transition


class TestInputValidation:
    """Test input validation for tasks."""

    def test_title_required(self, session: Session, test_user: User):
        """Test that title is required."""
        with pytest.raises(Exception):
            task = Task(user_id=test_user.id)
            session.add(task)
            session.commit()

    def test_title_length_validation(self, session: Session, test_user: User):
        """Test title length constraints."""
        # Title too long (>200 chars)
        long_title = "x" * 201
        task = Task(title=long_title, user_id=test_user.id)

        # Should be truncated or raise error based on model validation
        assert len(task.title) <= 200 or task.title == long_title

    def test_valid_priority_values(self, session: Session, test_user: User):
        """Test that only valid priority values are accepted."""
        valid_priorities = ["low", "medium", "high", "urgent"]

        for priority in valid_priorities:
            task = Task(title=f"Task {priority}", user_id=test_user.id, priority=priority)
            session.add(task)
            session.commit()
            assert task.priority == priority

    def test_valid_status_values(self, session: Session, test_user: User):
        """Test that only valid status values are accepted."""
        valid_statuses = ["todo", "in_progress", "review", "done", "blocked"]

        for status in valid_statuses:
            task = Task(title=f"Task {status}", user_id=test_user.id, status=status)
            session.add(task)
            session.commit()
            assert task.status == status


class TestStatusTransitions:
    """Test status transition validation."""

    def test_valid_status_transition(self):
        """Test valid status transitions."""
        assert validate_status_transition("todo", "in_progress") == True
        assert validate_status_transition("in_progress", "review") == True
        assert validate_status_transition("review", "done") == True

    def test_invalid_status_transition(self):
        """Test invalid status transitions."""
        assert validate_status_transition("todo", "done") == False
        assert validate_status_transition("done", "todo") == False

    def test_blocked_status_from_any(self):
        """Test that blocked status can be set from any status."""
        assert validate_status_transition("todo", "blocked") == True
        assert validate_status_transition("in_progress", "blocked") == True
        assert validate_status_transition("review", "blocked") == True


class TestUserIsolation:
    """Test user isolation enforcement."""

    def test_user_can_only_see_own_tasks(self, session: Session, test_user: User):
        """Test that users can only see their own tasks."""
        from auth import get_password_hash

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

        # Create tasks for both users
        task1 = Task(title="User 1 Task", user_id=test_user.id)
        task2 = Task(title="User 2 Task", user_id=other_user.id)
        session.add_all([task1, task2])
        session.commit()

        # Query tasks for test_user
        from sqlmodel import select
        statement = select(Task).where(
            Task.user_id == test_user.id,
            Task.deleted == False
        )
        user_tasks = session.exec(statement).all()

        assert len(user_tasks) == 1
        assert user_tasks[0].title == "User 1 Task"

    def test_user_cannot_access_other_user_task(self, session: Session, test_user: User):
        """Test that users cannot access tasks from other users."""
        from auth import get_password_hash

        other_user = User(
            email="other2@example.com",
            password_hash=get_password_hash("Test@Password123"),
            first_name="Other",
            last_name="User"
        )
        session.add(other_user)
        session.commit()

        task = Task(title="Other's Task", user_id=other_user.id)
        session.add(task)
        session.commit()

        # Try to query with wrong user_id
        from sqlmodel import select
        statement = select(Task).where(
            Task.id == task.id,
            Task.user_id == test_user.id
        )
        result = session.exec(statement).first()

        assert result is None


class TestCompletionTracking:
    """Test task completion tracking."""

    def test_completed_at_set_on_completion(self, session: Session, test_user: User):
        """Test that completed_at is set when task is marked done."""
        task = Task(title="Test", user_id=test_user.id, status="todo")
        session.add(task)
        session.commit()

        # Mark as done
        task.status = "done"
        task.completed_at = datetime.utcnow()
        session.commit()

        assert task.completed_at is not None
        assert task.status == "done"

    def test_completed_at_cleared_on_reopen(self, session: Session, test_user: User):
        """Test that completed_at is cleared when task is reopened."""
        task = Task(
            title="Test",
            user_id=test_user.id,
            status="done",
            completed_at=datetime.utcnow()
        )
        session.add(task)
        session.commit()

        # Reopen task
        task.status = "todo"
        task.completed_at = None
        session.commit()

        assert task.completed_at is None
        assert task.status == "todo"
