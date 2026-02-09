"""
Cache warming job for analytics.

This job pre-populates the cache for active users to improve
dashboard load times.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List
from sqlmodel import Session, select
from database import get_session
from models import User
from services.analytics import (
    calculate_task_totals,
    calculate_completion_rate,
    calculate_priority_distribution,
    calculate_status_distribution,
    calculate_productivity_score
)
from services.cache import cache_metric
import logging

logger = logging.getLogger(__name__)


async def get_active_users(session: Session, days: int = 7) -> List[User]:
    """
    Get users who have been active in the last N days.

    Args:
        session: Database session
        days: Number of days to look back

    Returns:
        List of active users
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    statement = select(User).where(
        User.last_login_at >= cutoff_date,
        User.is_active == True
    )

    result = session.exec(statement)
    return result.all()


async def warm_user_cache(session: Session, user_id: str) -> None:
    """
    Pre-populate cache for a single user.

    Args:
        session: Database session
        user_id: User ID to warm cache for
    """
    try:
        logger.info(f"Warming cache for user {user_id}")

        # Calculate and cache task totals
        totals = await calculate_task_totals(session, user_id)
        await cache_metric(session, user_id, "task_totals", totals)

        # Calculate and cache completion rate
        completion_rate = await calculate_completion_rate(session, user_id)
        await cache_metric(session, user_id, "completion_rate", {"rate": completion_rate})

        # Calculate and cache priority distribution
        priority_dist = await calculate_priority_distribution(session, user_id)
        await cache_metric(session, user_id, "priority_distribution", priority_dist)

        # Calculate and cache status distribution
        status_dist = await calculate_status_distribution(session, user_id)
        await cache_metric(session, user_id, "status_distribution", status_dist)

        # Calculate and cache productivity score
        productivity = await calculate_productivity_score(session, user_id)
        await cache_metric(session, user_id, "productivity_score", {"score": productivity})

        logger.info(f"✓ Cache warmed for user {user_id}")

    except Exception as e:
        logger.error(f"✗ Failed to warm cache for user {user_id}: {e}")


async def warm_cache_for_active_users(days: int = 7, batch_size: int = 10) -> dict:
    """
    Warm cache for all active users.

    Args:
        days: Number of days to look back for active users
        batch_size: Number of users to process in parallel

    Returns:
        Summary of cache warming operation
    """
    start_time = datetime.utcnow()

    with next(get_session()) as session:
        # Get active users
        active_users = await get_active_users(session, days)
        total_users = len(active_users)

        logger.info(f"Starting cache warming for {total_users} active users")

        # Process users in batches
        success_count = 0
        error_count = 0

        for i in range(0, total_users, batch_size):
            batch = active_users[i:i + batch_size]

            # Process batch in parallel
            tasks = [warm_user_cache(session, str(user.id)) for user in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count successes and errors
            for result in results:
                if isinstance(result, Exception):
                    error_count += 1
                else:
                    success_count += 1

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        summary = {
            "total_users": total_users,
            "success_count": success_count,
            "error_count": error_count,
            "duration_seconds": duration,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat()
        }

        logger.info(f"Cache warming completed: {summary}")

        return summary


async def refresh_materialized_views() -> None:
    """
    Refresh all materialized views for analytics.
    """
    try:
        logger.info("Refreshing materialized views")

        with next(get_session()) as session:
            # Refresh user task stats
            session.exec("REFRESH MATERIALIZED VIEW CONCURRENTLY user_task_stats")

            # Refresh priority distribution
            session.exec("REFRESH MATERIALIZED VIEW CONCURRENTLY user_priority_distribution")

            # Refresh status distribution
            session.exec("REFRESH MATERIALIZED VIEW CONCURRENTLY user_status_distribution")

            # Refresh monthly trends
            session.exec("REFRESH MATERIALIZED VIEW CONCURRENTLY user_monthly_trends")

            session.commit()

        logger.info("✓ Materialized views refreshed")

    except Exception as e:
        logger.error(f"✗ Failed to refresh materialized views: {e}")
        raise


async def run_cache_warming_job() -> dict:
    """
    Main entry point for cache warming job.

    This should be scheduled to run periodically (e.g., every hour).

    Returns:
        Summary of the job execution
    """
    logger.info("=" * 60)
    logger.info("Starting cache warming job")
    logger.info("=" * 60)

    try:
        # Refresh materialized views first
        await refresh_materialized_views()

        # Warm cache for active users
        summary = await warm_cache_for_active_users(days=7, batch_size=10)

        logger.info("=" * 60)
        logger.info("Cache warming job completed successfully")
        logger.info("=" * 60)

        return summary

    except Exception as e:
        logger.error(f"Cache warming job failed: {e}")
        raise


if __name__ == "__main__":
    # Run the cache warming job
    asyncio.run(run_cache_warming_job())
