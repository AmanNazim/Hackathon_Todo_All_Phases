"""
Caching service for analytics metrics.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_

from models import AnalyticsCache


# Default cache TTL in minutes
DEFAULT_CACHE_TTL = 5


async def cache_metric(
    db: AsyncSession,
    user_id: UUID,
    metric_name: str,
    metric_value: Dict[str, Any],
    ttl_minutes: int = DEFAULT_CACHE_TTL
) -> None:
    """
    Cache a metric value for a user.

    Args:
        db: Database session
        user_id: User ID
        metric_name: Name of the metric to cache
        metric_value: Metric value as a dictionary
        ttl_minutes: Time to live in minutes (default: 5)
    """
    expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)

    # Check if cache entry already exists
    stmt = select(AnalyticsCache).where(
        and_(
            AnalyticsCache.user_id == user_id,
            AnalyticsCache.metric_name == metric_name
        )
    )
    result = await db.execute(stmt)
    existing_cache = result.scalar_one_or_none()

    if existing_cache:
        # Update existing cache entry
        existing_cache.metric_value = metric_value
        existing_cache.expires_at = expires_at
        existing_cache.created_at = datetime.utcnow()
    else:
        # Create new cache entry
        cache_entry = AnalyticsCache(
            user_id=user_id,
            metric_name=metric_name,
            metric_value=metric_value,
            expires_at=expires_at
        )
        db.add(cache_entry)

    await db.commit()


async def get_cached_metric(
    db: AsyncSession,
    user_id: UUID,
    metric_name: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a cached metric value for a user.

    Args:
        db: Database session
        user_id: User ID
        metric_name: Name of the metric to retrieve

    Returns:
        Cached metric value or None if not found or expired
    """
    now = datetime.utcnow()

    stmt = select(AnalyticsCache).where(
        and_(
            AnalyticsCache.user_id == user_id,
            AnalyticsCache.metric_name == metric_name,
            AnalyticsCache.expires_at > now
        )
    )

    result = await db.execute(stmt)
    cache_entry = result.scalar_one_or_none()

    if cache_entry:
        return cache_entry.metric_value

    return None


async def invalidate_cache(
    db: AsyncSession,
    user_id: UUID,
    metric_name: Optional[str] = None
) -> int:
    """
    Invalidate cached metrics for a user.

    Args:
        db: Database session
        user_id: User ID
        metric_name: Specific metric to invalidate, or None to invalidate all

    Returns:
        Number of cache entries deleted
    """
    if metric_name:
        # Invalidate specific metric
        stmt = delete(AnalyticsCache).where(
            and_(
                AnalyticsCache.user_id == user_id,
                AnalyticsCache.metric_name == metric_name
            )
        )
    else:
        # Invalidate all metrics for user
        stmt = delete(AnalyticsCache).where(
            AnalyticsCache.user_id == user_id
        )

    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount


async def cleanup_expired_cache(db: AsyncSession) -> int:
    """
    Clean up expired cache entries.

    Args:
        db: Database session

    Returns:
        Number of expired entries deleted
    """
    now = datetime.utcnow()

    stmt = delete(AnalyticsCache).where(
        AnalyticsCache.expires_at <= now
    )

    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount


async def get_or_compute_metric(
    db: AsyncSession,
    user_id: UUID,
    metric_name: str,
    compute_func,
    ttl_minutes: int = DEFAULT_CACHE_TTL,
    **compute_kwargs
) -> Dict[str, Any]:
    """
    Get a metric from cache or compute it if not cached.

    Args:
        db: Database session
        user_id: User ID
        metric_name: Name of the metric
        compute_func: Async function to compute the metric
        ttl_minutes: Cache TTL in minutes
        **compute_kwargs: Additional arguments for compute function

    Returns:
        Metric value (from cache or freshly computed)
    """
    # Try to get from cache first
    cached_value = await get_cached_metric(db, user_id, metric_name)

    if cached_value is not None:
        return cached_value

    # Compute the metric
    computed_value = await compute_func(db, user_id, **compute_kwargs)

    # Cache the result
    await cache_metric(db, user_id, metric_name, computed_value, ttl_minutes)

    return computed_value


async def invalidate_user_cache_on_task_change(
    db: AsyncSession,
    user_id: UUID
) -> None:
    """
    Invalidate all analytics cache for a user when tasks change.

    This should be called after task creation, update, or deletion.

    Args:
        db: Database session
        user_id: User ID
    """
    await invalidate_cache(db, user_id)
