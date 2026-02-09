"""
Unit tests for task CRUD operations.
"""
import pytest
from datetime import datetime, timedelta
from sqlmodel import Session
from models import Task, User


class TestTaskCreation:
    """Test task creation operations."""

    def test_create_task_success(self, session: Session, test_user: User):
        """Test successful task creation."""
        task = Task(
            title="Test Task",
            description="Test Description",
            user_id=test_user.id,
            priority="high",
            status="todo"
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.id is not None
        assert task.title == "Test Task"
        assert task.user_id == test_user.id
        assert task.deleted == False

    def test_create_task_with_due_date(self, session: Session, test_user: User):
        """Test task creation with due date."""
        due_date = datetime.utcnow() + timedelta(days=7)
        task = Task(
            title="Task with due date",
            user_id=test_user.id,
            due_date=due_date
        )
        session.add(task)
        session.commit()

        assert task.due_date == due_date


class TestTaskRetrieval:
    """Test task retrieval operations."""

    def test_get_task_by_id(self, session: Session, test_user: User):
        """Test retrieving task by ID."""
        task = Task(title="Test Task", user_id=test_user.id)
        session.add(task)
        session.commit()

        retrieved = session.get(Task, task.id)
        assert retrieved is not None
        assert retrieved.title == "Test Task"

    def test_get_user_tasks(self, session: Session, test_user: User):
        """Test retrieving all tasks for a user."""
        for i in range(5):
            task = Task(title=f"Task {i}", user_id=test_user.id)
            session.add(task)
        session.commit()

        from sqlmodel import select
        statement = select(Task).where(
            Task.user_id == test_user.id,
            Task.deleted == False
        )
        tasks = session.exec(statement).all()

        assert len(tasks) == 5


class TestTaskUpdate:
    """Test task update operations."""

    def test_update_task_title(self, session: Session, test_user: User):
        """Test updating task title."""
        task = Task(title="Original", user_id=test_user.id)
        session.add(task)
        session.commit()

        task.title = "Updated"
        session.commit()
        session.refresh(task)

        assert task.title == "Updated"

    def test_update_task_status(self, session: Session, test_user: User):
        """Test updating task status."""
        task = Task(title="Test", user_id=test_user.id, status="todo")
        session.add(task)
        session.commit()

        task.status = "done"
        task.completed_at = datetime.utcnow()
        session.commit()

        assert task.status == "done"
        assert task.completed_at is not None


class TestTaskDeletion:
    """Test task deletion operations."""

    def test_soft_delete_task(self, session: Session, test_user: User):
        """Test soft deletion of task."""
        task = Task(title="To Delete", user_id=test_user.id)
        session.add(task)
        session.commit()

        task.deleted = True
        task.deleted_at = datetime.utcnow()
        session.commit()

        assert task.deleted == True
        assert task.deleted_at is not None

    def test_deleted_tasks_not_in_list(self, session: Session, test_user: User):
        """Test that deleted tasks don't appear in normal queries."""
        task1 = Task(title="Active", user_id=test_user.id)
        task2 = Task(title="Deleted", user_id=test_user.id, deleted=True)
        session.add_all([task1, task2])
        session.commit()

        from sqlmodel import select
        statement = select(Task).where(
            Task.user_id == test_user.id,
            Task.deleted == False
        )
        tasks = session.exec(statement).all()

        assert len(tasks) == 1
        assert tasks[0].title == "Active"
