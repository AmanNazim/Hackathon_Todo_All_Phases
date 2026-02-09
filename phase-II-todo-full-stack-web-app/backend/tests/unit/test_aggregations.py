"""
Unit tests for analytics aggregations.

Tests daily aggregation, period grouping, and statistics calculations.
"""

import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select
from services.analytics import (
    aggregate_by_period,
    calculate_trends,
    get_date_range
)
from jobs.daily_aggregation import (
    aggregate_user_stats,
    run_daily_aggregation
)
from models import Task, DailyAnalytics, User


class TestDailyAggregation:
    """Test suite for daily aggregation job."""

    def test_aggregate_user_stats_basic(self, session: Session, test_user: User):
        """Test basic user stats aggregation."""
        now = datetime.utcnow()
        today = now.date()

        # Create tasks for today
        for i in range(10):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done" if i < 7 else "todo",
                created_at=now,
                completed_at=now if i < 7 else None
            )
            session.add(task)
        session.commit()

        # Run aggregation
        aggregate_user_stats(session, test_user.id, today)

        # Check aggregated data
        statement = select(DailyAnalytics).where(
            DailyAnalytics.user_id == test_user.id,
            DailyAnalytics.date == today
        )
        analytics = session.exec(statement).first()

        assert analytics is not None
        assert analytics.tasks_created == 10
        assert analytics.tasks_completed == 7
        assert analytics.completion_rate == 70.0

    def test_aggregate_user_stats_no_tasks(self, session: Session, test_user: User):
        """Test aggregation when user has no tasks."""
        today = datetime.utcnow().date()

        # Run aggregation
        aggregate_user_stats(session, test_user.id, today)

        # Check aggregated data
        statement = select(DailyAnalytics).where(
            DailyAnalytics.user_id == test_user.id,
            DailyAnalytics.date == today
        )
        analytics = session.exec(statement).first()

        assert analytics is not None
        assert analytics.tasks_created == 0
        assert analytics.tasks_completed == 0
        assert analytics.completion_rate == 0.0

    def test_aggregate_user_stats_updates_existing(self, session: Session, test_user: User):
        """Test that aggregation updates existing records."""
        today = datetime.utcnow().date()

        # Create initial analytics record
        initial_analytics = DailyAnalytics(
            user_id=test_user.id,
            date=today,
            tasks_created=5,
            tasks_completed=3,
            completion_rate=60.0
        )
        session.add(initial_analytics)
        session.commit()

        # Create more tasks
        now = datetime.utcnow()
        for i in range(5):
            task = Task(
                title=f"New Task {i}",
                user_id=test_user.id,
                status="done",
                created_at=now,
                completed_at=now
            )
            session.add(task)
        session.commit()

        # Run aggregation again
        aggregate_user_stats(session, test_user.id, today)

        # Check updated data
        statement = select(DailyAnalytics).where(
            DailyAnalytics.user_id == test_user.id,
            DailyAnalytics.date == today
        )
        analytics = session.exec(statement).first()

        assert analytics.tasks_created == 10  # 5 + 5
        assert analytics.tasks_completed == 8  # 3 + 5


class TestPeriodGrouping:
    """Test suite for period-based grouping."""

    def test_aggregate_by_period_daily(self, session: Session, test_user: User):
        """Test daily period aggregation."""
        now = datetime.utcnow()

        # Create analytics for last 7 days
        for i in range(7):
            date = (now - timedelta(days=i)).date()
            analytics = DailyAnalytics(
                user_id=test_user.id,
                date=date,
                tasks_created=10,
                tasks_completed=7,
                completion_rate=70.0
            )
            session.add(analytics)
        session.commit()

        # Aggregate by daily period
        start_date = (now - timedelta(days=6)).date()
        end_date = now.date()

        results = aggregate_by_period(
            session,
            test_user.id,
            "daily",
            start_date,
            end_date
        )

        assert len(results) == 7
        assert all(r["tasks_created"] == 10 for r in results)
        assert all(r["tasks_completed"] == 7 for r in results)

    def test_aggregate_by_period_weekly(self, session: Session, test_user: User):
        """Test weekly period aggregation."""
        now = datetime.utcnow()

        # Create analytics for last 28 days (4 weeks)
        for i in range(28):
            date = (now - timedelta(days=i)).date()
            analytics = DailyAnalytics(
                user_id=test_user.id,
                date=date,
                tasks_created=5,
                tasks_completed=3,
                completion_rate=60.0
            )
            session.add(analytics)
        session.commit()

        # Aggregate by weekly period
        start_date = (now - timedelta(days=27)).date()
        end_date = now.date()

        results = aggregate_by_period(
            session,
            test_user.id,
            "weekly",
            start_date,
            end_date
        )

        assert len(results) == 4  # 4 weeks
        # Each week should have 7 days * 5 tasks = 35 tasks created
        assert all(r["tasks_created"] == 35 for r in results)

    def test_aggregate_by_period_monthly(self, session: Session, test_user: User):
        """Test monthly period aggregation."""
        now = datetime.utcnow()

        # Create analytics for last 60 days (2 months)
        for i in range(60):
            date = (now - timedelta(days=i)).date()
            analytics = DailyAnalytics(
                user_id=test_user.id,
                date=date,
                tasks_created=2,
                tasks_completed=1,
                completion_rate=50.0
            )
            session.add(analytics)
        session.commit()

        # Aggregate by monthly period
        start_date = (now - timedelta(days=59)).date()
        end_date = now.date()

        results = aggregate_by_period(
            session,
            test_user.id,
            "monthly",
            start_date,
            end_date
        )

        assert len(results) >= 2  # At least 2 months


class TestTrendsCalculation:
    """Test suite for trends calculations."""

    def test_calculate_trends_increasing(self, session: Session, test_user: User):
        """Test trends calculation with increasing values."""
        now = datetime.utcnow()

        # Create analytics with increasing completion rate
        for i in range(7):
            date = (now - timedelta(days=6-i)).date()
            analytics = DailyAnalytics(
                user_id=test_user.id,
                date=date,
                tasks_created=10,
                tasks_completed=i+1,  # Increasing from 1 to 7
                completion_rate=(i+1) * 10.0
            )
            session.add(analytics)
        session.commit()

        # Calculate trends
        start_date = (now - timedelta(days=6)).date()
        end_date = now.date()

        trends = calculate_trends(
            session,
            test_user.id,
            "daily",
            start_date,
            end_date
        )

        assert len(trends) == 7
        # Completion rate should be increasing
        rates = [t["completion_rate"] for t in trends]
        assert rates == sorted(rates)  # Should be in ascending order

    def test_calculate_trends_empty_period(self, session: Session, test_user: User):
        """Test trends calculation with no data."""
        now = datetime.utcnow()
        start_date = (now - timedelta(days=6)).date()
        end_date = now.date()

        trends = calculate_trends(
            session,
            test_user.id,
            "daily",
            start_date,
            end_date
        )

        # Should return empty list or zeros
        assert isinstance(trends, list)


class TestDateRangeCalculation:
    """Test suite for date range calculations."""

    def test_get_date_range_last_7_days(self):
        """Test date range for last 7 days."""
        start_date, end_date = get_date_range("7days")

        assert end_date == datetime.utcnow().date()
        assert start_date == (datetime.utcnow() - timedelta(days=6)).date()
        assert (end_date - start_date).days == 6

    def test_get_date_range_last_30_days(self):
        """Test date range for last 30 days."""
        start_date, end_date = get_date_range("30days")

        assert end_date == datetime.utcnow().date()
        assert start_date == (datetime.utcnow() - timedelta(days=29)).date()
        assert (end_date - start_date).days == 29

    def test_get_date_range_last_90_days(self):
        """Test date range for last 90 days."""
        start_date, end_date = get_date_range("90days")

        assert end_date == datetime.utcnow().date()
        assert start_date == (datetime.utcnow() - timedelta(days=89)).date()
        assert (end_date - start_date).days == 89

    def test_get_date_range_custom(self):
        """Test custom date range."""
        custom_start = datetime(2024, 1, 1).date()
        custom_end = datetime(2024, 1, 31).date()

        start_date, end_date = get_date_range("custom", custom_start, custom_end)

        assert start_date == custom_start
        assert end_date == custom_end


class TestAggregationAccuracy:
    """Test suite for aggregation accuracy."""

    def test_aggregation_matches_raw_data(self, session: Session, test_user: User):
        """Test that aggregated data matches raw task data."""
        now = datetime.utcnow()
        today = now.date()

        # Create known set of tasks
        tasks_created = 15
        tasks_completed = 10
        tasks_deleted = 2

        for i in range(tasks_created):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done" if i < tasks_completed else "todo",
                created_at=now,
                completed_at=now if i < tasks_completed else None,
                deleted=i < tasks_deleted
            )
            session.add(task)
        session.commit()

        # Run aggregation
        aggregate_user_stats(session, test_user.id, today)

        # Verify aggregated data
        statement = select(DailyAnalytics).where(
            DailyAnalytics.user_id == test_user.id,
            DailyAnalytics.date == today
        )
        analytics = session.exec(statement).first()

        assert analytics.tasks_created == tasks_created
        assert analytics.tasks_completed == tasks_completed
        assert analytics.tasks_deleted == tasks_deleted

        # Calculate expected completion rate
        active_tasks = tasks_created - tasks_deleted
        expected_rate = (tasks_completed / active_tasks * 100) if active_tasks > 0 else 0
        assert abs(analytics.completion_rate - expected_rate) < 0.01
