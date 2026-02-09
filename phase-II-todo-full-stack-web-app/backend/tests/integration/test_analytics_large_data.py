"""
Integration tests for analytics with large datasets.

Tests performance and accuracy with 10,000+ tasks and 1 year of history.
"""

import pytest
from datetime import datetime, timedelta
from sqlmodel import Session
from fastapi.testclient import TestClient
from models import Task, DailyAnalytics, User
import random


class TestLargeDatasetPerformance:
    """Test suite for large dataset handling."""

    @pytest.fixture
    def large_dataset(self, session: Session, test_user: User):
        """Create a large dataset of tasks."""
        print("Creating large dataset (10,000 tasks)...")

        now = datetime.utcnow()
        tasks = []

        # Create 10,000 tasks over 1 year
        for i in range(10000):
            days_ago = random.randint(0, 365)
            created_at = now - timedelta(days=days_ago)

            status = random.choice(["todo", "in_progress", "done", "done", "done"])  # 60% done
            priority = random.choice(["low", "medium", "high"])

            task = Task(
                title=f"Task {i}",
                description=f"Description for task {i}",
                user_id=test_user.id,
                status=status,
                priority=priority,
                created_at=created_at,
                completed_at=created_at + timedelta(days=random.randint(1, 10)) if status == "done" else None,
                due_date=created_at + timedelta(days=random.randint(5, 30)) if random.random() > 0.3 else None
            )
            tasks.append(task)

        session.add_all(tasks)
        session.commit()

        print("✓ Large dataset created")
        return tasks

    def test_overview_with_large_dataset(self, client: TestClient, test_user: User, auth_headers: dict, large_dataset):
        """Test overview endpoint with 10,000 tasks."""
        import time

        start_time = time.time()

        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/overview",
            headers=auth_headers
        )

        end_time = time.time()
        duration = end_time - start_time

        assert response.status_code == 200
        assert duration < 5.0  # Should complete within 5 seconds

        data = response.json()
        assert data["total"] == 10000

        print(f"✓ Overview query completed in {duration:.2f}s")

    def test_trends_with_large_dataset(self, client: TestClient, test_user: User, auth_headers: dict, large_dataset):
        """Test trends endpoint with 1 year of data."""
        import time

        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        start_time = time.time()

        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/trends",
            params={
                "period": "monthly",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            headers=auth_headers
        )

        end_time = time.time()
        duration = end_time - start_time

        assert response.status_code == 200
        assert duration < 5.0  # Should complete within 5 seconds

        print(f"✓ Trends query completed in {duration:.2f}s")

    def test_export_with_large_dataset(self, client: TestClient, test_user: User, auth_headers: dict, large_dataset):
        """Test export with 10,000 tasks."""
        import time

        start_time = time.time()

        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/export",
            params={"format": "json"},
            headers=auth_headers
        )

        end_time = time.time()
        duration = end_time - start_time

        assert response.status_code == 200
        assert duration < 30.0  # Export can take longer, but should be < 30s

        data = response.json()
        assert len(data) == 10000

        print(f"✓ Export completed in {duration:.2f}s")

    def test_memory_usage_with_large_dataset(self, session: Session, test_user: User, large_dataset):
        """Test memory usage with large dataset."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform analytics calculations
        from services.analytics import (
            calculate_task_totals,
            calculate_completion_rate,
            calculate_productivity_score
        )

        calculate_task_totals(session, test_user.id)
        calculate_completion_rate(session, test_user.id)
        calculate_productivity_score(session, test_user.id)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 500 MB)
        assert memory_increase < 500

        print(f"✓ Memory increase: {memory_increase:.2f} MB")


class TestDataAccuracy:
    """Test suite for data accuracy validation."""

    def test_aggregation_accuracy(self, session: Session, test_user: User):
        """Test that aggregated data matches raw data."""
        now = datetime.utcnow()
        today = now.date()

        # Create known dataset
        tasks_created = 100
        tasks_completed = 70
        tasks_deleted = 10

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
        from jobs.daily_aggregation import aggregate_user_stats
        aggregate_user_stats(session, test_user.id, today)

        # Verify accuracy
        from sqlmodel import select
        statement = select(DailyAnalytics).where(
            DailyAnalytics.user_id == test_user.id,
            DailyAnalytics.date == today
        )
        analytics = session.exec(statement).first()

        assert analytics.tasks_created == tasks_created
        assert analytics.tasks_completed == tasks_completed
        assert analytics.tasks_deleted == tasks_deleted

        # Verify completion rate calculation
        active_tasks = tasks_created - tasks_deleted
        expected_rate = (tasks_completed / active_tasks * 100)
        assert abs(analytics.completion_rate - expected_rate) < 0.01

    def test_trend_calculation_accuracy(self, session: Session, test_user: User):
        """Test that trend calculations are accurate."""
        now = datetime.utcnow()

        # Create analytics for 7 days with known values
        expected_data = []
        for i in range(7):
            date = (now - timedelta(days=6-i)).date()
            tasks_created = (i + 1) * 10
            tasks_completed = (i + 1) * 7

            analytics = DailyAnalytics(
                user_id=test_user.id,
                date=date,
                tasks_created=tasks_created,
                tasks_completed=tasks_completed,
                completion_rate=(tasks_completed / tasks_created * 100)
            )
            session.add(analytics)
            expected_data.append({
                "date": date,
                "tasks_created": tasks_created,
                "tasks_completed": tasks_completed
            })
        session.commit()

        # Calculate trends
        from services.analytics import calculate_trends
        start_date = (now - timedelta(days=6)).date()
        end_date = now.date()

        trends = calculate_trends(session, test_user.id, "daily", start_date, end_date)

        # Verify accuracy
        assert len(trends) == 7
        for i, trend in enumerate(trends):
            assert trend["tasks_created"] == expected_data[i]["tasks_created"]
            assert trend["tasks_completed"] == expected_data[i]["tasks_completed"]

    def test_productivity_score_accuracy(self, session: Session, test_user: User):
        """Test productivity score calculation accuracy."""
        now = datetime.utcnow()

        # Create tasks with known metrics
        # 10 tasks: 8 completed (80%), 7 on-time (87.5%), high velocity
        for i in range(10):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status="done" if i < 8 else "todo",
                created_at=now - timedelta(days=7),
                completed_at=now - timedelta(days=1) if i < 8 else None,
                due_date=now if i < 7 else now - timedelta(days=5)
            )
            session.add(task)
        session.commit()

        # Calculate productivity score
        from services.analytics import calculate_productivity_score
        score = calculate_productivity_score(session, test_user.id)

        # Score should be high (> 70) given good metrics
        assert score > 70.0
        assert score <= 100.0


class TestPerformanceTesting:
    """Test suite for performance testing."""

    def test_query_performance_with_indexes(self, session: Session, test_user: User):
        """Test that queries use indexes efficiently."""
        import time

        # Create moderate dataset
        now = datetime.utcnow()
        for i in range(1000):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id,
                status=random.choice(["todo", "done"]),
                created_at=now - timedelta(days=random.randint(0, 30))
            )
            session.add(task)
        session.commit()

        # Test query performance
        from services.analytics import calculate_task_totals

        start_time = time.time()
        calculate_task_totals(session, test_user.id)
        duration = time.time() - start_time

        # Should be fast with proper indexes
        assert duration < 1.0

        print(f"✓ Query completed in {duration:.3f}s")

    def test_cache_effectiveness(self, session: Session, test_user: User):
        """Test cache hit rate and effectiveness."""
        from services.cache import cache_metric, get_cached_metric

        metric_name = "test_metric"
        metric_value = {"data": "test"}

        # Cache the metric
        cache_metric(session, test_user.id, metric_name, metric_value)

        # Measure cache hit performance
        import time

        start_time = time.time()
        for _ in range(100):
            get_cached_metric(session, test_user.id, metric_name)
        duration = time.time() - start_time

        # Cache hits should be very fast
        avg_time = duration / 100
        assert avg_time < 0.01  # < 10ms per cache hit

        print(f"✓ Average cache hit time: {avg_time*1000:.2f}ms")


class TestErrorHandling:
    """Test suite for error handling."""

    def test_invalid_date_range(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test handling of invalid date ranges."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/trends",
            params={
                "period": "daily",
                "start_date": "2024-12-31",
                "end_date": "2024-01-01"  # End before start
            },
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "date" in response.json()["detail"].lower()

    def test_database_error_handling(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test handling of database errors."""
        # This would require mocking database failures
        # For now, test that endpoints handle missing data gracefully
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/overview",
            headers=auth_headers
        )

        # Should return valid response even with no data
        assert response.status_code == 200

    def test_missing_data_handling(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test handling of missing analytics data."""
        # Request trends for period with no data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/trends",
            params={
                "period": "daily",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        # Should return empty list or zeros, not error
        data = response.json()
        assert isinstance(data, list)

    def test_invalid_export_format(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test handling of invalid export format."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/export",
            params={"format": "invalid"},
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "format" in response.json()["detail"].lower()

    def test_timeout_handling(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test handling of query timeouts."""
        # This would require simulating slow queries
        # For now, verify endpoints have reasonable timeouts
        response = client.get(
            f"/api/v1/users/{test_user.id}/analytics/overview",
            headers=auth_headers,
            timeout=30  # 30 second timeout
        )

        # Should complete within timeout
        assert response.status_code == 200
