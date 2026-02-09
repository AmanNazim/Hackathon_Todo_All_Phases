"""
Analytics service for calculating task statistics and metrics.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.sql import extract

from models import Task, DailyAnalytics


async def calculate_task_totals(db: AsyncSession, user_id: UUID) -> Dict[str, int]:
    """
    Calculate total, completed, and pending task counts for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dictionary with total, completed, and pending counts
    """
    # Get total tasks
    total_stmt = select(func.count(Task.id)).where(Task.user_id == user_id)
    total_result = await db.execute(total_stmt)
    total = total_result.scalar() or 0

    # Get completed tasks
    completed_stmt = select(func.count(Task.id)).where(
        and_(Task.user_id == user_id, Task.completed == True)
    )
    completed_result = await db.execute(completed_stmt)
    completed = completed_result.scalar() or 0

    # Calculate pending
    pending = total - completed

    return {
        "total": total,
        "completed": completed,
        "pending": pending
    }


async def get_completion_stats(db: AsyncSession, user_id: UUID) -> Dict[str, int]:
    """
    Get completion statistics for different time periods.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dictionary with completion counts for today, this week, and this month
    """
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = datetime(now.year, now.month, 1)

    # Tasks completed today
    today_stmt = select(func.count(Task.id)).where(
        and_(
            Task.user_id == user_id,
            Task.completed == True,
            Task.updated_at >= today_start
        )
    )
    today_result = await db.execute(today_stmt)
    today_count = today_result.scalar() or 0

    # Tasks completed this week
    week_stmt = select(func.count(Task.id)).where(
        and_(
            Task.user_id == user_id,
            Task.completed == True,
            Task.updated_at >= week_start
        )
    )
    week_result = await db.execute(week_stmt)
    week_count = week_result.scalar() or 0

    # Tasks completed this month
    month_stmt = select(func.count(Task.id)).where(
        and_(
            Task.user_id == user_id,
            Task.completed == True,
            Task.updated_at >= month_start
        )
    )
    month_result = await db.execute(month_stmt)
    month_count = month_result.scalar() or 0

    return {
        "today": today_count,
        "this_week": week_count,
        "this_month": month_count
    }


async def calculate_completion_rate(db: AsyncSession, user_id: UUID) -> float:
    """
    Calculate the overall completion rate for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Completion rate as a percentage (0-100)
    """
    totals = await calculate_task_totals(db, user_id)

    if totals["total"] == 0:
        return 0.0

    return round((totals["completed"] / totals["total"]) * 100, 2)


async def get_priority_distribution(db: AsyncSession, user_id: UUID) -> Dict[str, int]:
    """
    Get task count distribution by priority.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dictionary with counts for each priority level
    """
    stmt = select(Task.priority, func.count(Task.id)).where(
        Task.user_id == user_id
    ).group_by(Task.priority)

    result = await db.execute(stmt)
    rows = result.all()

    # Initialize with all priorities
    distribution = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "urgent": 0
    }

    # Update with actual counts
    for priority, count in rows:
        distribution[priority] = count

    return distribution


async def get_status_distribution(db: AsyncSession, user_id: UUID) -> Dict[str, int]:
    """
    Get task count distribution by status (completed vs pending).

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dictionary with counts for completed and pending tasks
    """
    totals = await calculate_task_totals(db, user_id)

    return {
        "completed": totals["completed"],
        "pending": totals["pending"]
    }


async def get_overdue_count(db: AsyncSession, user_id: UUID) -> int:
    """
    Get count of overdue tasks.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Number of overdue tasks
    """
    now = datetime.utcnow()

    stmt = select(func.count(Task.id)).where(
        and_(
            Task.user_id == user_id,
            Task.completed == False,
            Task.due_date < now,
            Task.due_date.isnot(None)
        )
    )

    result = await db.execute(stmt)
    return result.scalar() or 0


async def calculate_average_completion_time(db: AsyncSession, user_id: UUID) -> Optional[str]:
    """
    Calculate average time to complete tasks.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Average completion time as a string (e.g., "2.5 days") or None
    """
    stmt = select(
        func.avg(
            extract('epoch', Task.updated_at - Task.created_at)
        )
    ).where(
        and_(
            Task.user_id == user_id,
            Task.completed == True
        )
    )

    result = await db.execute(stmt)
    avg_seconds = result.scalar()

    if not avg_seconds:
        return None

    # Convert seconds to days
    avg_days = avg_seconds / (24 * 3600)

    if avg_days < 1:
        avg_hours = avg_seconds / 3600
        return f"{avg_hours:.1f} hours"
    else:
        return f"{avg_days:.1f} days"


async def calculate_detailed_completion_time(db: AsyncSession, user_id: UUID) -> Dict[str, Any]:
    """
    Calculate detailed completion time analytics including average, min, max by priority.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dictionary with detailed completion time statistics
    """
    # Get all completed tasks with completion times
    stmt = select(
        Task.priority,
        extract('epoch', Task.updated_at - Task.created_at).label('completion_seconds')
    ).where(
        and_(
            Task.user_id == user_id,
            Task.completed == True
        )
    )

    result = await db.execute(stmt)
    tasks = result.all()

    if not tasks:
        return {
            "average": None,
            "by_priority": {},
            "total_completed": 0
        }

    # Calculate overall statistics
    completion_times = [t.completion_seconds for t in tasks]
    avg_seconds = sum(completion_times) / len(completion_times)
    min_seconds = min(completion_times)
    max_seconds = max(completion_times)

    # Calculate by priority
    by_priority = {}
    for priority in ["low", "medium", "high", "urgent"]:
        priority_times = [t.completion_seconds for t in tasks if t.priority == priority]
        if priority_times:
            avg_priority = sum(priority_times) / len(priority_times)
            by_priority[priority] = {
                "average_seconds": avg_priority,
                "average_formatted": _format_seconds(avg_priority),
                "count": len(priority_times)
            }

    return {
        "average_seconds": avg_seconds,
        "average_formatted": _format_seconds(avg_seconds),
        "min_seconds": min_seconds,
        "min_formatted": _format_seconds(min_seconds),
        "max_seconds": max_seconds,
        "max_formatted": _format_seconds(max_seconds),
        "by_priority": by_priority,
        "total_completed": len(tasks)
    }


def _format_seconds(seconds: float) -> str:
    """Format seconds into human-readable time string."""
    days = seconds / (24 * 3600)
    if days >= 1:
        return f"{days:.1f} days"

    hours = seconds / 3600
    if hours >= 1:
        return f"{hours:.1f} hours"

    minutes = seconds / 60
    return f"{minutes:.1f} minutes"


async def calculate_trends(
    db: AsyncSession,
    user_id: UUID,
    period: str = "weekly",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict]:
    """
    Calculate task trends over time.

    Args:
        db: Database session
        user_id: User ID
        period: Period type (daily, weekly, monthly)
        start_date: Start date for analysis
        end_date: End date for analysis

    Returns:
        List of trend data points
    """
    if not end_date:
        end_date = datetime.utcnow()

    if not start_date:
        if period == "daily":
            start_date = end_date - timedelta(days=30)
        elif period == "weekly":
            start_date = end_date - timedelta(weeks=12)
        else:  # monthly
            start_date = end_date - timedelta(days=365)

    # Query daily analytics data
    stmt = select(DailyAnalytics).where(
        and_(
            DailyAnalytics.user_id == user_id,
            DailyAnalytics.date >= start_date.date(),
            DailyAnalytics.date <= end_date.date()
        )
    ).order_by(DailyAnalytics.date)

    result = await db.execute(stmt)
    analytics = result.scalars().all()

    # Format data points
    data_points = []
    for record in analytics:
        data_points.append({
            "date": record.date.isoformat(),
            "tasks_created": record.tasks_created,
            "tasks_completed": record.tasks_completed,
            "completion_rate": float(record.completion_rate) if record.completion_rate else 0.0
        })

    return data_points


async def calculate_adherence_rate(db: AsyncSession, user_id: UUID, period_days: int = 30) -> Dict:
    """
    Calculate due date adherence rate.

    Args:
        db: Database session
        user_id: User ID
        period_days: Number of days to analyze

    Returns:
        Dictionary with adherence statistics
    """
    start_date = datetime.utcnow() - timedelta(days=period_days)

    # Get tasks with due dates that were completed in the period
    stmt = select(Task).where(
        and_(
            Task.user_id == user_id,
            Task.completed == True,
            Task.due_date.isnot(None),
            Task.updated_at >= start_date
        )
    )

    result = await db.execute(stmt)
    tasks = result.scalars().all()

    if not tasks:
        return {
            "on_time": 0,
            "late": 0,
            "adherence_rate": 0.0,
            "average_delay": None
        }

    on_time = 0
    late = 0
    total_delay_seconds = 0

    for task in tasks:
        if task.updated_at <= task.due_date:
            on_time += 1
        else:
            late += 1
            delay = (task.updated_at - task.due_date).total_seconds()
            total_delay_seconds += delay

    total_with_due_date = on_time + late
    adherence_rate = (on_time / total_with_due_date * 100) if total_with_due_date > 0 else 0.0

    average_delay = None
    if late > 0:
        avg_delay_days = (total_delay_seconds / late) / (24 * 3600)
        average_delay = f"{avg_delay_days:.1f} days"

    return {
        "on_time": on_time,
        "late": late,
        "adherence_rate": round(adherence_rate, 2),
        "average_delay": average_delay
    }


async def calculate_task_velocity(db: AsyncSession, user_id: UUID, weeks: int = 4) -> float:
    """
    Calculate task velocity (tasks completed per week).

    Args:
        db: Database session
        user_id: User ID
        weeks: Number of weeks to analyze

    Returns:
        Tasks completed per week
    """
    start_date = datetime.utcnow() - timedelta(weeks=weeks)

    stmt = select(func.count(Task.id)).where(
        and_(
            Task.user_id == user_id,
            Task.completed == True,
            Task.updated_at >= start_date
        )
    )

    result = await db.execute(stmt)
    completed_count = result.scalar() or 0

    return round(completed_count / weeks, 2)


async def calculate_productivity_score(
    db: AsyncSession,
    user_id: UUID
) -> Dict:
    """
    Calculate overall productivity score based on multiple factors.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dictionary with productivity score and factors
    """
    # Get completion rate (40% weight)
    completion_rate = await calculate_completion_rate(db, user_id)

    # Get adherence rate (30% weight)
    adherence_data = await calculate_adherence_rate(db, user_id, 30)
    adherence_rate = adherence_data["adherence_rate"]

    # Get velocity score (30% weight)
    velocity = await calculate_task_velocity(db, user_id, 4)
    # Normalize velocity to 0-100 scale (assume 10 tasks/week is 100)
    velocity_score = min(velocity * 10, 100)

    # Calculate weighted score
    score = (
        completion_rate * 0.4 +
        adherence_rate * 0.3 +
        velocity_score * 0.3
    )

    return {
        "score": round(score, 2),
        "factors": {
            "completion_rate": round(completion_rate, 2),
            "due_date_adherence": round(adherence_rate, 2),
            "task_velocity": round(velocity_score, 2)
        }
    }


async def compare_periods(
    db: AsyncSession,
    user_id: UUID,
    current_start: datetime,
    current_end: datetime,
    previous_start: datetime,
    previous_end: datetime
) -> Dict[str, Any]:
    """
    Compare analytics metrics between two time periods.

    Args:
        db: Database session
        user_id: User ID
        current_start: Start date of current period
        current_end: End date of current period
        previous_start: Start date of previous period
        previous_end: End date of previous period

    Returns:
        Dictionary with comparison data
    """
    # Get tasks for current period
    current_stmt = select(Task).where(
        and_(
            Task.user_id == user_id,
            Task.created_at >= current_start,
            Task.created_at <= current_end
        )
    )
    current_result = await db.execute(current_stmt)
    current_tasks = current_result.scalars().all()

    # Get tasks for previous period
    previous_stmt = select(Task).where(
        and_(
            Task.user_id == user_id,
            Task.created_at >= previous_start,
            Task.created_at <= previous_end
        )
    )
    previous_result = await db.execute(previous_stmt)
    previous_tasks = previous_result.scalars().all()

    # Calculate metrics for both periods
    current_total = len(current_tasks)
    current_completed = sum(1 for t in current_tasks if t.completed)
    current_rate = (current_completed / current_total * 100) if current_total > 0 else 0

    previous_total = len(previous_tasks)
    previous_completed = sum(1 for t in previous_tasks if t.completed)
    previous_rate = (previous_completed / previous_total * 100) if previous_total > 0 else 0

    # Calculate changes
    total_change = current_total - previous_total
    completed_change = current_completed - previous_completed
    rate_change = current_rate - previous_rate

    return {
        "current_period": {
            "start": current_start.isoformat(),
            "end": current_end.isoformat(),
            "total_tasks": current_total,
            "completed_tasks": current_completed,
            "completion_rate": round(current_rate, 2)
        },
        "previous_period": {
            "start": previous_start.isoformat(),
            "end": previous_end.isoformat(),
            "total_tasks": previous_total,
            "completed_tasks": previous_completed,
            "completion_rate": round(previous_rate, 2)
        },
        "changes": {
            "total_tasks": total_change,
            "completed_tasks": completed_change,
            "completion_rate": round(rate_change, 2),
            "total_tasks_percent": round((total_change / previous_total * 100) if previous_total > 0 else 0, 2),
            "completed_tasks_percent": round((completed_change / previous_completed * 100) if previous_completed > 0 else 0, 2)
        }
    }


async def calculate_trend_direction(
    db: AsyncSession,
    user_id: UUID,
    metric: str = "completion_rate",
    periods: int = 4
) -> str:
    """
    Calculate trend direction for a metric over multiple periods.

    Args:
        db: Database session
        user_id: User ID
        metric: Metric to analyze (completion_rate, velocity, adherence)
        periods: Number of periods to analyze

    Returns:
        Trend direction: "increasing", "decreasing", or "stable"
    """
    # Get data for the last N periods (weeks)
    end_date = datetime.utcnow()
    period_data = []

    for i in range(periods):
        period_end = end_date - timedelta(weeks=i)
        period_start = period_end - timedelta(weeks=1)

        if metric == "completion_rate":
            # Calculate completion rate for this period
            stmt = select(Task).where(
                and_(
                    Task.user_id == user_id,
                    Task.created_at >= period_start,
                    Task.created_at <= period_end
                )
            )
            result = await db.execute(stmt)
            tasks = result.scalars().all()

            total = len(tasks)
            completed = sum(1 for t in tasks if t.completed)
            value = (completed / total * 100) if total > 0 else 0

        elif metric == "velocity":
            # Calculate velocity for this period
            stmt = select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.completed == True,
                    Task.updated_at >= period_start,
                    Task.updated_at <= period_end
                )
            )
            result = await db.execute(stmt)
            value = result.scalar() or 0

        else:
            # Default to 0 for unknown metrics
            value = 0

        period_data.append(value)

    # Reverse to get chronological order
    period_data.reverse()

    # Calculate trend
    if len(period_data) < 2:
        return "stable"

    # Simple linear trend detection
    increases = 0
    decreases = 0

    for i in range(1, len(period_data)):
        if period_data[i] > period_data[i-1]:
            increases += 1
        elif period_data[i] < period_data[i-1]:
            decreases += 1

    if increases > decreases:
        return "increasing"
    elif decreases > increases:
        return "decreasing"
    else:
        return "stable"


async def get_date_range(period: str, end_date: Optional[datetime] = None) -> tuple:
    """
    Get start and end dates for a given period.

    Args:
        period: Period type (7days, 30days, 90days, year, week, month)
        end_date: Optional end date (defaults to now)

    Returns:
        Tuple of (start_date, end_date)
    """
    if not end_date:
        end_date = datetime.utcnow()

    period_map = {
        "7days": timedelta(days=7),
        "30days": timedelta(days=30),
        "90days": timedelta(days=90),
        "year": timedelta(days=365),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "quarter": timedelta(days=90)
    }

    delta = period_map.get(period, timedelta(days=30))
    start_date = end_date - delta

    return (start_date, end_date)
