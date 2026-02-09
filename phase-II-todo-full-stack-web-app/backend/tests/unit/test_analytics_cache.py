"""
Unit tests for analytics caching.

Tests cache hit/miss, expiration, and invalidation.
"""

import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select
from services.cache import (
    cache_metric,
    get_cached_metric,
    invalidate_cache,
    invalidate_user_cache
)
from models import AnalyticsCache, User


class TestCacheOperations:
    """Test suite for basic cache operations."""

    def test_cache_metric_creates_entry(self, session: Session, test_user: User):
        """Test that caching a metric creates a cache entry."""
        metric_name = "test_metric"
        metric_value = {"count": 42, "rate": 85.5}

        cache_metric(session, test_user.id, metric_name, metric_value)

        # Verify cache entry exists
        statement = select(AnalyticsCache).where(
            AnalyticsCache.user_id == test_user.id,
            AnalyticsCache.metric_name == metric_name
        )
        cache_entry = session.exec(statement).first()

        assert cache_entry is not None
        assert cache_entry.metric_value == metric_value

    def test_cache_metric_updates_existing(self, session: Session, test_user: User):
        """Test that caching updates existing entries."""
        metric_name = "test_metric"
        initial_value = {"count": 10}
        updated_value = {"count": 20}

        # Cache initial value
        cache_metric(session, test_user.id, metric_name, initial_value)

        # Cache updated value
        cache_metric(session, test_user.id, metric_name, updated_value)

        # Verify only one entry exists with updated value
        statement = select(AnalyticsCache).where(
            AnalyticsCache.user_id == test_user.id,
            AnalyticsCache.metric_name == metric_name
        )
        cache_entries = session.exec(statement).all()

        assert len(cache_entries) == 1
        assert cache_entries[0].metric_value == updated_value

    def test_get_cached_metric_hit(self, session: Session, test_user: User):
        """Test cache hit when metric exists."""
        metric_name = "test_metric"
        metric_value = {"data": "test"}

        # Cache the metric
        cache_metric(session, test_user.id, metric_name, metric_value)

        # Retrieve from cache
        cached_value = get_cached_metric(session, test_user.id, metric_name)

        assert cached_value == metric_value

    def test_get_cached_metric_miss(self, session: Session, test_user: User):
        """Test cache miss when metric doesn't exist."""
        cached_value = get_cached_metric(session, test_user.id, "nonexistent_metric")

        assert cached_value is None

    def test_get_cached_metric_expired(self, session: Session, test_user: User):
        """Test that expired cache entries return None."""
        metric_name = "test_metric"
        metric_value = {"data": "test"}

        # Create expired cache entry
        cache_entry = AnalyticsCache(
            user_id=test_user.id,
            metric_name=metric_name,
            metric_value=metric_value,
            expires_at=datetime.utcnow() - timedelta(minutes=1)  # Expired 1 minute ago
        )
        session.add(cache_entry)
        session.commit()

        # Try to retrieve
        cached_value = get_cached_metric(session, test_user.id, metric_name)

        assert cached_value is None


class TestCacheExpiration:
    """Test suite for cache expiration."""

    def test_cache_has_expiration_time(self, session: Session, test_user: User):
        """Test that cached metrics have expiration time."""
        metric_name = "test_metric"
        metric_value = {"data": "test"}

        cache_metric(session, test_user.id, metric_name, metric_value, ttl_minutes=5)

        # Verify expiration time is set
        statement = select(AnalyticsCache).where(
            AnalyticsCache.user_id == test_user.id,
            AnalyticsCache.metric_name == metric_name
        )
        cache_entry = session.exec(statement).first()

        assert cache_entry.expires_at is not None
        assert cache_entry.expires_at > datetime.utcnow()

    def test_cache_custom_ttl(self, session: Session, test_user: User):
        """Test caching with custom TTL."""
        metric_name = "test_metric"
        metric_value = {"data": "test"}
        ttl_minutes = 10

        cache_metric(session, test_user.id, metric_name, metric_value, ttl_minutes=ttl_minutes)

        # Verify expiration time
        statement = select(AnalyticsCache).where(
            AnalyticsCache.user_id == test_user.id,
            AnalyticsCache.metric_name == metric_name
        )
        cache_entry = session.exec(statement).first()

        expected_expiry = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        # Allow 1 minute margin for test execution time
        assert abs((cache_entry.expires_at - expected_expiry).total_seconds()) < 60

    def test_expired_entries_not_returned(self, session: Session, test_user: User):
        """Test that expired entries are not returned."""
        # Create multiple cache entries, some expired
        metrics = [
            ("metric1", {"data": "1"}, datetime.utcnow() + timedelta(minutes=5)),  # Valid
            ("metric2", {"data": "2"}, datetime.utcnow() - timedelta(minutes=1)),  # Expired
            ("metric3", {"data": "3"}, datetime.utcnow() + timedelta(minutes=10)), # Valid
        ]

        for name, value, expires_at in metrics:
            cache_entry = AnalyticsCache(
                user_id=test_user.id,
                metric_name=name,
                metric_value=value,
                expires_at=expires_at
            )
            session.add(cache_entry)
        session.commit()

        # Try to retrieve each metric
        result1 = get_cached_metric(session, test_user.id, "metric1")
        result2 = get_cached_metric(session, test_user.id, "metric2")
        result3 = get_cached_metric(session, test_user.id, "metric3")

        assert result1 == {"data": "1"}  # Valid
        assert result2 is None  # Expired
        assert result3 == {"data": "3"}  # Valid


class TestCacheInvalidation:
    """Test suite for cache invalidation."""

    def test_invalidate_single_metric(self, session: Session, test_user: User):
        """Test invalidating a single metric."""
        metric_name = "test_metric"
        metric_value = {"data": "test"}

        # Cache the metric
        cache_metric(session, test_user.id, metric_name, metric_value)

        # Invalidate it
        invalidate_cache(session, test_user.id, metric_name)

        # Verify it's gone
        cached_value = get_cached_metric(session, test_user.id, metric_name)
        assert cached_value is None

    def test_invalidate_nonexistent_metric(self, session: Session, test_user: User):
        """Test invalidating a metric that doesn't exist."""
        # Should not raise an error
        invalidate_cache(session, test_user.id, "nonexistent_metric")

    def test_invalidate_user_cache_all_metrics(self, session: Session, test_user: User):
        """Test invalidating all metrics for a user."""
        # Cache multiple metrics
        metrics = [
            ("metric1", {"data": "1"}),
            ("metric2", {"data": "2"}),
            ("metric3", {"data": "3"}),
        ]

        for name, value in metrics:
            cache_metric(session, test_user.id, name, value)

        # Invalidate all user cache
        invalidate_user_cache(session, test_user.id)

        # Verify all are gone
        for name, _ in metrics:
            cached_value = get_cached_metric(session, test_user.id, name)
            assert cached_value is None

    def test_invalidate_user_cache_preserves_other_users(self, session: Session, test_user: User):
        """Test that invalidating one user's cache doesn't affect others."""
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

        # Cache metrics for both users
        cache_metric(session, test_user.id, "metric1", {"data": "user1"})
        cache_metric(session, other_user.id, "metric1", {"data": "user2"})

        # Invalidate test_user's cache
        invalidate_user_cache(session, test_user.id)

        # Verify test_user's cache is gone
        assert get_cached_metric(session, test_user.id, "metric1") is None

        # Verify other_user's cache is intact
        assert get_cached_metric(session, other_user.id, "metric1") == {"data": "user2"}


class TestCachePerformance:
    """Test suite for cache performance characteristics."""

    def test_cache_reduces_database_queries(self, session: Session, test_user: User):
        """Test that cache reduces database queries."""
        metric_name = "expensive_metric"
        metric_value = {"result": "computed"}

        # First call - cache miss, should compute and cache
        cache_metric(session, test_user.id, metric_name, metric_value)

        # Second call - cache hit, should return cached value
        cached_value = get_cached_metric(session, test_user.id, metric_name)

        assert cached_value == metric_value

    def test_cache_handles_large_values(self, session: Session, test_user: User):
        """Test that cache can handle large metric values."""
        metric_name = "large_metric"
        # Create a large metric value
        metric_value = {
            "data": [{"id": i, "value": f"item_{i}"} for i in range(1000)]
        }

        cache_metric(session, test_user.id, metric_name, metric_value)

        # Retrieve and verify
        cached_value = get_cached_metric(session, test_user.id, metric_name)

        assert cached_value == metric_value
        assert len(cached_value["data"]) == 1000


class TestCacheIsolation:
    """Test suite for cache isolation between users."""

    def test_cache_isolated_by_user(self, session: Session, test_user: User):
        """Test that cache entries are isolated by user."""
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

        # Cache same metric name for both users with different values
        cache_metric(session, test_user.id, "metric", {"user": "test"})
        cache_metric(session, other_user.id, "metric", {"user": "other"})

        # Verify each user gets their own value
        test_value = get_cached_metric(session, test_user.id, "metric")
        other_value = get_cached_metric(session, other_user.id, "metric")

        assert test_value == {"user": "test"}
        assert other_value == {"user": "other"}

    def test_cache_invalidation_isolated_by_user(self, session: Session, test_user: User):
        """Test that cache invalidation is isolated by user."""
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

        # Cache for both users
        cache_metric(session, test_user.id, "metric", {"user": "test"})
        cache_metric(session, other_user.id, "metric", {"user": "other"})

        # Invalidate test_user's metric
        invalidate_cache(session, test_user.id, "metric")

        # Verify test_user's is gone but other_user's remains
        assert get_cached_metric(session, test_user.id, "metric") is None
        assert get_cached_metric(session, other_user.id, "metric") == {"user": "other"}
