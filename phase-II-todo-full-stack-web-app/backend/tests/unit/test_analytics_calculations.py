"""
Unit tests for analytics calculations.

Tests completion rate, trends, productivity score, and other metric calculations.
"""

import pytest
from datetime import datetime, timedelta
from sqlmodel import Session
from services.analytics import (
    calculate_completion_rate,
    calculate_productivity_score,
    calculate_task_velocity,
    calculate_adherence_rate,
    calculate_average_completion_time,
    calculate_trend_direction
)
from models import Task, User


class TestCompletionRateCalculation:
    """Test suite for completion rate calculations."""

    def test_completion_rate_all_completed(self, session: Session, test_user: User):
        """Test completion rate when all tasks are completed."""
        # Create 10 completed tasks
        for i in range(10):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done"
            )
            session.add(task)
        session.commit()

        rate = calculate_completion_rate(session, test_user.id)
        assert rate == 100.0

    def test_completion_rate_none_completed(self, session: Session, test_user: User):
        """Test completion rate when no tasks are completed."""
        # Create 10 pending tasks
        for i in range(10):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="todo"
            )
            session.add(task)
        session.commit()

        rate = calculate_completion_rate(session, test_user.id)
        assert rate == 0.0

    def test_completion_rate_partial(self, session: Session, test_user: User):
        """Test completion rate with partial completion."""
        # Create 7 completed and 3 pending tasks
        for i in range(7):
            task = Task(
                title=f"Completed {i}",
                user_id=test_user.id,
                status="done"
            )
            session.add(task)

        for i in range(3):
            task = Task(
                title=f"Pending {i}",
                user_id=test_user.id,
                status="todo"
            )
            session.add(task)

        session.commit()

        rate = calculate_completion_rate(session, test_user.id)
        assert rate == 70.0

    def test_completion_rate_no_tasks(self, session: Session, test_user: User):
        """Test completion rate when user has no tasks."""
        rate = calculate_completion_rate(session, test_user.id)
        assert rate == 0.0

    def test_completion_rate_excludes_deleted(self, session: Session, test_user: User):
        """Test that deleted tasks are excluded from calculation."""
        # Create 5 completed, 3 pending, 2 deleted
        for i in range(5):
            task = Task(
                title=f"Completed {i}",
                user_id=test_user.id,
                status="done"
            )
            session.add(task)

        for i in range(3):
            task = Task(
                title=f"Pending {i}",
                user_id=test_user.id,
                status="todo"
            )
            session.add(task)

        for i in range(2):
            task = Task(
                title=f"Deleted {i}",
                user_id=test_user.id,
                status="done",
                deleted=True
            )
            session.add(task)

        session.commit()

        rate = calculate_completion_rate(session, test_user.id)
        # Should be 5/(5+3) = 62.5%
        assert rate == 62.5


class TestProductivityScoreCalculation:
    """Test suite for productivity score calculations."""

    def test_productivity_score_perfect(self, session: Session, test_user: User):
        """Test productivity score with perfect metrics."""
        # Create tasks with 100% completion, 100% adherence, high velocity
        now = datetime.utcnow()

        # 10 completed tasks, all on time
        for i in range(10):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done",
                due_date=now + timedelta(days=1),
                completed_at=now,
                created_at=now - timedelta(days=7)
            )
            session.add(task)

        session.commit()

        score = calculate_productivity_score(session, test_user.id)
        assert score >= 90.0  # Should be very high

    def test_productivity_score_poor(self, session: Session, test_user: User):
        """Test productivity score with poor metrics."""
        now = datetime.utcnow()

        # 2 completed, 8 pending, all overdue
        for i in range(2):
            task = Task(
                title=f"Completed {i}",
                user_id=test_user.id,
                status="done",
                due_date=now - timedelta(days=5),
                completed_at=now,
                created_at=now - timedelta(days=30)
            )
            session.add(task)

        for i in range(8):
            task = Task(
                title=f"Overdue {i}",
                user_id=test_user.id,
                status="todo",
                due_date=now - timedelta(days=10),
                created_at=now - timedelta(days=30)
            )
            session.add(task)

        session.commit()

        score = calculate_productivity_score(session, test_user.id)
        assert score < 50.0  # Should be low

    def test_productivity_score_no_tasks(self, session: Session, test_user: User):
        """Test productivity score when user has no tasks."""
        score = calculate_productivity_score(session, test_user.id)
        assert score == 0.0


class TestTaskVelocityCalculation:
    """Test suite for task velocity calculations."""

    def test_velocity_one_week(self, session: Session, test_user: User):
        """Test velocity calculation for one week."""
        now = datetime.utcnow()

        # Create 7 tasks completed in the last week
        for i in range(7):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done",
                completed_at=now - timedelta(days=i),
                created_at=now - timedelta(days=i+1)
            )
            session.add(task)

        session.commit()

        velocity = calculate_task_velocity(session, test_user.id, days=7)
        assert velocity == 7.0  # 7 tasks per week

    def test_velocity_multiple_weeks(self, session: Session, test_user: User):
        """Test velocity calculation over multiple weeks."""
        now = datetime.utcnow()

        # Create 20 tasks completed over 4 weeks
        for i in range(20):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done",
                completed_at=now - timedelta(days=i),
                created_at=now - timedelta(days=i+1)
            )
            session.add(task)

        session.commit()

        velocity = calculate_task_velocity(session, test_user.id, days=28)
        assert velocity == 5.0  # 20 tasks / 4 weeks = 5 per week

    def test_velocity_no_completed_tasks(self, session: Session, test_user: User):
        """Test velocity when no tasks are completed."""
        velocity = calculate_task_velocity(session, test_user.id, days=7)
        assert velocity == 0.0


class TestAdherenceRateCalculation:
    """Test suite for due date adherence calculations."""

    def test_adherence_all_on_time(self, session: Session, test_user: User):
        """Test adherence when all tasks completed on time."""
        now = datetime.utcnow()

        # Create 10 tasks completed before due date
        for i in range(10):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done",
                due_date=now + timedelta(days=1),
                completed_at=now,
                created_at=now - timedelta(days=7)
            )
            session.add(task)

        session.commit()

        adherence = calculate_adherence_rate(session, test_user.id)
        assert adherence == 100.0

    def test_adherence_all_late(self, session: Session, test_user: User):
        """Test adherence when all tasks completed late."""
        now = datetime.utcnow()

        # Create 10 tasks completed after due date
        for i in range(10):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done",
                due_date=now - timedelta(days=5),
                completed_at=now,
                created_at=now - timedelta(days=10)
            )
            session.add(task)

        session.commit()

        adherence = calculate_adherence_rate(session, test_user.id)
        assert adherence == 0.0

    def test_adherence_partial(self, session: Session, test_user: User):
        """Test adherence with mixed on-time and late tasks."""
        now = datetime.utcnow()

        # 6 on-time, 4 late
        for i in range(6):
            task = Task(
                title=f"On-time {i}",
                user_id=test_user.id,
                status="done",
                due_date=now + timedelta(days=1),
                completed_at=now,
                created_at=now - timedelta(days=7)
            )
            session.add(task)

        for i in range(4):
            task = Task(
                title=f"Late {i}",
                user_id=test_user.id,
                status="done",
                due_date=now - timedelta(days=5),
                completed_at=now,
                created_at=now - timedelta(days=10)
            )
            session.add(task)

        session.commit()

        adherence = calculate_adherence_rate(session, test_user.id)
        assert adherence == 60.0

    def test_adherence_no_due_dates(self, session: Session, test_user: User):
        """Test adherence when tasks have no due dates."""
        # Create tasks without due dates
        for i in range(5):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done",
                completed_at=datetime.utcnow(),
                created_at=datetime.utcnow() - timedelta(days=7)
            )
            session.add(task)

        session.commit()

        adherence = calculate_adherence_rate(session, test_user.id)
        assert adherence == 0.0  # No tasks with due dates


class TestCompletionTimeCalculation:
    """Test suite for completion time calculations."""

    def test_average_completion_time(self, session: Session, test_user: User):
        """Test average completion time calculation."""
        now = datetime.utcnow()

        # Create tasks with known completion times
        completion_times = [1, 2, 3, 4, 5]  # days

        for days in completion_times:
            task = Task(
                title=f"Task {days}d",
                user_id=test_user.id,
                status="done",
                created_at=now - timedelta(days=days),
                completed_at=now
            )
            session.add(task)

        session.commit()

        avg_time = calculate_average_completion_time(session, test_user.id)
        assert avg_time == 3.0  # Average of 1,2,3,4,5 = 3

    def test_completion_time_no_completed_tasks(self, session: Session, test_user: User):
        """Test completion time when no tasks are completed."""
        avg_time = calculate_average_completion_time(session, test_user.id)
        assert avg_time == 0.0


class TestTrendDirectionCalculation:
    """Test suite for trend direction calculations."""

    def test_trend_direction_increasing(self):
        """Test trend direction for increasing values."""
        current = 80.0
        previous = 60.0

        direction = calculate_trend_direction(current, previous)
        assert direction == "up"

    def test_trend_direction_decreasing(self):
        """Test trend direction for decreasing values."""
        current = 50.0
        previous = 70.0

        direction = calculate_trend_direction(current, previous)
        assert direction == "down"

    def test_trend_direction_stable(self):
        """Test trend direction for stable values."""
        current = 65.0
        previous = 65.0

        direction = calculate_trend_direction(current, previous)
        assert direction == "stable"

    def test_trend_direction_no_previous(self):
        """Test trend direction when no previous value."""
        current = 75.0
        previous = None

        direction = calculate_trend_direction(current, previous)
        assert direction == "stable"
