"""
Daily aggregation job for analytics data.

This job runs daily to aggregate task statistics and store them in the daily_analytics table
for efficient historical trend analysis.
"""

from datetime import datetime, timedelta
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from models import Task, DailyAnalytics, User
from database import get_db


async def aggregate_user_daily_stats(
    db: AsyncSession,
    user_id: UUID,
    date: datetime
) -> DailyAnalytics:
    """
    Aggregate daily statistics for a specific user and date.

    Args:
        db: Database session
        user_id: User ID
        date: Date to aggregate (will use date component only)

    Returns:
        DailyAnalytics record
    """
    target_date = date.date()
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())

    # Count tasks created on this date
    created_stmt = select(func.count(Task.id)).where(
        and_(
            Task.user_id == user_id,
            Task.created_at >= start_of_day,
            Task.created_at <= end_of_day
        )
    )
    created_result = await db.execute(created_stmt)
    tasks_created = created_result.scalar() or 0

    # Count tasks completed on this date
    completed_stmt = select(func.count(Task.id)).where(
        and_(
            Task.user_id == user_id,
            Task.completed == True,
            Task.updated_at >= start_of_day,
            Task.updated_at <= end_of_day
        )
    )
    completed_result = await db.execute(completed_stmt)
    tasks_completed = completed_result.scalar() or 0

    # Count tasks deleted on this date (we don't track deletions currently, so this is 0)
    tasks_deleted = 0

    # Calculate completion rate for the day
    completion_rate = 0.0
    if tasks_created > 0:
        completion_rate = (tasks_completed / tasks_created) * 100

    # Check if record already exists
    existing_stmt = select(DailyAnalytics).where(
        and_(
            DailyAnalytics.user_id == user_id,
            DailyAnalytics.date == target_date
        )
    )
    existing_result = await db.execute(existing_stmt)
    existing_record = existing_result.scalar_one_or_none()

    if existing_record:
        # Update existing record
        existing_record.tasks_created = tasks_created
        existing_record.tasks_completed = tasks_completed
        existing_record.tasks_deleted = tasks_deleted
        existing_record.completion_rate = completion_rate
        existing_record.updated_at = datetime.utcnow()
        daily_analytics = existing_record
    else:
        # Create new record
        daily_analytics = DailyAnalytics(
            user_id=user_id,
            date=target_date,
            tasks_created=tasks_created,
            tasks_completed=tasks_completed,
            tasks_deleted=tasks_deleted,
            completion_rate=completion_rate
        )
        db.add(daily_analytics)

    await db.commit()
    await db.refresh(daily_analytics)

    return daily_analytics


async def aggregate_all_users_daily_stats(
    db: AsyncSession,
    date: datetime
) -> int:
    """
    Aggregate daily statistics for all active users.

    Args:
        db: Database session
        date: Date to aggregate

    Returns:
        Number of users processed
    """
    # Get all active users
    users_stmt = select(User).where(User.is_active == True)
    users_result = await db.execute(users_stmt)
    users = users_result.scalars().all()

    count = 0
    for user in users:
        await aggregate_user_daily_stats(db, user.id, date)
        count += 1

    return count


async def run_daily_aggregation_job(db: AsyncSession) -> dict:
    """
    Run the daily aggregation job for yesterday's data.

    This should be scheduled to run daily at midnight UTC.

    Args:
        db: Database session

    Returns:
        Dictionary with job execution results
    """
    # Aggregate yesterday's data
    yesterday = datetime.utcnow() - timedelta(days=1)

    try:
        users_processed = await aggregate_all_users_daily_stats(db, yesterday)

        return {
            "status": "success",
            "date": yesterday.date().isoformat(),
            "users_processed": users_processed,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "date": yesterday.date().isoformat(),
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def backfill_daily_analytics(
    db: AsyncSession,
    user_id: UUID,
    start_date: datetime,
    end_date: datetime
) -> int:
    """
    Backfill daily analytics data for a user over a date range.

    Useful for populating historical data or fixing gaps.

    Args:
        db: Database session
        user_id: User ID
        start_date: Start date for backfill
        end_date: End date for backfill

    Returns:
        Number of days processed
    """
    current_date = start_date
    days_processed = 0

    while current_date <= end_date:
        await aggregate_user_daily_stats(db, user_id, current_date)
        days_processed += 1
        current_date += timedelta(days=1)

    return days_processed


async def backfill_all_users_analytics(
    db: AsyncSession,
    days_back: int = 30
) -> dict:
    """
    Backfill analytics data for all users for the past N days.

    Args:
        db: Database session
        days_back: Number of days to backfill

    Returns:
        Dictionary with backfill results
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_back)

    # Get all active users
    users_stmt = select(User).where(User.is_active == True)
    users_result = await db.execute(users_stmt)
    users = users_result.scalars().all()

    total_days = 0
    users_processed = 0

    for user in users:
        days = await backfill_daily_analytics(db, user.id, start_date, end_date)
        total_days += days
        users_processed += 1

    return {
        "status": "success",
        "users_processed": users_processed,
        "total_days_processed": total_days,
        "date_range": {
            "start": start_date.date().isoformat(),
            "end": end_date.date().isoformat()
        },
        "timestamp": datetime.utcnow().isoformat()
    }
