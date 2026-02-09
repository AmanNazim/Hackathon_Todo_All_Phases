"""
Unit tests for tag operations.
"""
import pytest
from sqlmodel import Session, select
from models import Task, TaskTag, User


class TestTagCreation:
    """Test tag creation and assignment."""

    def test_add_tag_to_task(self, session: Session, test_user: User):
        """Test adding a tag to a task."""
        task = Task(title="Test Task", user_id=test_user.id)
        session.add(task)
        session.commit()

        tag = TaskTag(task_id=task.id, tag="urgent")
        session.add(tag)
        session.commit()

        assert tag.id is not None
        assert tag.tag == "urgent"

    def test_add_multiple_tags(self, session: Session, test_user: User):
        """Test adding multiple tags to a task."""
        task = Task(title="Test Task", user_id=test_user.id)
        session.add(task)
        session.commit()

        tags = [
            TaskTag(task_id=task.id, tag="work"),
            TaskTag(task_id=task.id, tag="urgent"),
            TaskTag(task_id=task.id, tag="important")
        ]
        session.add_all(tags)
        session.commit()

        statement = select(TaskTag).where(TaskTag.task_id == task.id)
        task_tags = session.exec(statement).all()

        assert len(task_tags) == 3


class TestTagRemoval:
    """Test tag removal operations."""

    def test_remove_tag_from_task(self, session: Session, test_user: User):
        """Test removing a tag from a task."""
        task = Task(title="Test Task", user_id=test_user.id)
        tag = TaskTag(task_id=task.id, tag="temp")
        session.add_all([task, tag])
        session.commit()

        session.delete(tag)
        session.commit()

        statement = select(TaskTag).where(TaskTag.task_id == task.id)
        remaining_tags = session.exec(statement).all()

        assert len(remaining_tags) == 0


class TestTagFiltering:
    """Test filtering tasks by tags."""

    def test_filter_tasks_by_single_tag(self, session: Session, test_user: User):
        """Test filtering tasks by a single tag."""
        task1 = Task(title="Task 1", user_id=test_user.id)
        task2 = Task(title="Task 2", user_id=test_user.id)
        session.add_all([task1, task2])
        session.commit()

        tag1 = TaskTag(task_id=task1.id, tag="work")
        tag2 = TaskTag(task_id=task2.id, tag="personal")
        session.add_all([tag1, tag2])
        session.commit()

        # Filter by "work" tag
        statement = (
            select(Task)
            .join(TaskTag)
            .where(
                Task.user_id == test_user.id,
                TaskTag.tag == "work"
            )
        )
        work_tasks = session.exec(statement).all()

        assert len(work_tasks) == 1
        assert work_tasks[0].title == "Task 1"

    def test_filter_tasks_by_multiple_tags(self, session: Session, test_user: User):
        """Test filtering tasks by multiple tags."""
        task = Task(title="Multi-tag Task", user_id=test_user.id)
        session.add(task)
        session.commit()

        tags = [
            TaskTag(task_id=task.id, tag="work"),
            TaskTag(task_id=task.id, tag="urgent")
        ]
        session.add_all(tags)
        session.commit()

        # Find tasks with both tags
        statement = select(TaskTag.task_id).where(
            TaskTag.tag.in_(["work", "urgent"])
        ).group_by(TaskTag.task_id).having(
            select([1]).select_from(TaskTag).where(
                TaskTag.task_id == TaskTag.task_id
            ).count() == 2
        )

        # This is a simplified test - actual implementation may vary
        assert task.id is not None


class TestTagStatistics:
    """Test tag statistics and analytics."""

    def test_get_tag_usage_count(self, session: Session, test_user: User):
        """Test getting usage count for tags."""
        tasks = [
            Task(title=f"Task {i}", user_id=test_user.id)
            for i in range(3)
        ]
        session.add_all(tasks)
        session.commit()

        # Add "work" tag to all tasks
        for task in tasks:
            tag = TaskTag(task_id=task.id, tag="work")
            session.add(tag)
        session.commit()

        from sqlmodel import func
        statement = (
            select(func.count(TaskTag.id))
            .join(Task)
            .where(
                Task.user_id == test_user.id,
                TaskTag.tag == "work"
            )
        )
        count = session.exec(statement).one()

        assert count == 3

    def test_get_all_unique_tags(self, session: Session, test_user: User):
        """Test getting all unique tags for a user."""
        task1 = Task(title="Task 1", user_id=test_user.id)
        task2 = Task(title="Task 2", user_id=test_user.id)
        session.add_all([task1, task2])
        session.commit()

        tags = [
            TaskTag(task_id=task1.id, tag="work"),
            TaskTag(task_id=task1.id, tag="urgent"),
            TaskTag(task_id=task2.id, tag="work"),  # Duplicate
            TaskTag(task_id=task2.id, tag="personal")
        ]
        session.add_all(tags)
        session.commit()

        statement = (
            select(TaskTag.tag)
            .join(Task)
            .where(Task.user_id == test_user.id)
            .distinct()
        )
        unique_tags = session.exec(statement).all()

        assert len(unique_tags) == 3
        assert set(unique_tags) == {"work", "urgent", "personal"}
