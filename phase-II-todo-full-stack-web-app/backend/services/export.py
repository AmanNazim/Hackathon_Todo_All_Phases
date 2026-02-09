"""
Export service for analytics data.

Provides functionality to export task and analytics data in various formats (CSV, JSON).
"""

import csv
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID
from io import StringIO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from models import Task


async def format_export_data(
    db: AsyncSession,
    user_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Format task data for export.

    Args:
        db: Database session
        user_id: User ID
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        List of task dictionaries formatted for export
    """
    # Build query
    query = select(Task).where(Task.user_id == user_id)

    if start_date:
        query = query.where(Task.created_at >= start_date)
    if end_date:
        query = query.where(Task.created_at <= end_date)

    query = query.order_by(Task.created_at.desc())

    # Execute query
    result = await db.execute(query)
    tasks = result.scalars().all()

    # Format data
    export_data = []
    for task in tasks:
        export_data.append({
            "id": str(task.id),
            "title": task.title,
            "description": task.description or "",
            "completed": task.completed,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else "",
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "completion_time": _calculate_completion_time(task) if task.completed else ""
        })

    return export_data


def _calculate_completion_time(task: Task) -> str:
    """
    Calculate time taken to complete a task.

    Args:
        task: Task object

    Returns:
        Completion time as a string
    """
    if not task.completed:
        return ""

    time_diff = task.updated_at - task.created_at
    days = time_diff.days
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds % 3600) // 60

    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


async def export_to_csv(
    db: AsyncSession,
    user_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> str:
    """
    Export task data to CSV format.

    Args:
        db: Database session
        user_id: User ID
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        CSV string
    """
    data = await format_export_data(db, user_id, start_date, end_date)

    if not data:
        # Return empty CSV with headers
        return "id,title,description,completed,priority,due_date,created_at,updated_at,completion_time\n"

    # Create CSV in memory
    output = StringIO()
    fieldnames = [
        "id", "title", "description", "completed", "priority",
        "due_date", "created_at", "updated_at", "completion_time"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

    return output.getvalue()


async def export_to_json(
    db: AsyncSession,
    user_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> str:
    """
    Export task data to JSON format.

    Args:
        db: Database session
        user_id: User ID
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        JSON string
    """
    data = await format_export_data(db, user_id, start_date, end_date)

    export_object = {
        "export_date": datetime.utcnow().isoformat(),
        "user_id": str(user_id),
        "filters": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "total_tasks": len(data),
        "tasks": data
    }

    return json.dumps(export_object, indent=2)


async def filter_export_data(
    data: List[Dict[str, Any]],
    filters: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Apply additional filters to export data.

    Args:
        data: List of task dictionaries
        filters: Dictionary of filter criteria

    Returns:
        Filtered list of task dictionaries
    """
    filtered_data = data

    # Filter by completion status
    if "completed" in filters:
        filtered_data = [
            task for task in filtered_data
            if task["completed"] == filters["completed"]
        ]

    # Filter by priority
    if "priority" in filters:
        priorities = filters["priority"] if isinstance(filters["priority"], list) else [filters["priority"]]
        filtered_data = [
            task for task in filtered_data
            if task["priority"] in priorities
        ]

    # Filter by date range
    if "start_date" in filters:
        start_date = datetime.fromisoformat(filters["start_date"])
        filtered_data = [
            task for task in filtered_data
            if datetime.fromisoformat(task["created_at"]) >= start_date
        ]

    if "end_date" in filters:
        end_date = datetime.fromisoformat(filters["end_date"])
        filtered_data = [
            task for task in filtered_data
            if datetime.fromisoformat(task["created_at"]) <= end_date
        ]

    return filtered_data


async def export_analytics_summary_csv(
    db: AsyncSession,
    user_id: UUID,
    analytics_data: Dict[str, Any]
) -> str:
    """
    Export analytics summary to CSV format.

    Args:
        db: Database session
        user_id: User ID
        analytics_data: Analytics data dictionary

    Returns:
        CSV string with analytics summary
    """
    output = StringIO()

    # Write summary section
    output.write("Analytics Summary\n")
    output.write(f"User ID,{user_id}\n")
    output.write(f"Export Date,{datetime.utcnow().isoformat()}\n")
    output.write("\n")

    # Write overview stats
    output.write("Metric,Value\n")
    output.write(f"Total Tasks,{analytics_data.get('total_tasks', 0)}\n")
    output.write(f"Completed Tasks,{analytics_data.get('completed_tasks', 0)}\n")
    output.write(f"Pending Tasks,{analytics_data.get('pending_tasks', 0)}\n")
    output.write(f"Completion Rate,{analytics_data.get('completion_rate', 0)}%\n")
    output.write(f"Overdue Tasks,{analytics_data.get('overdue_tasks', 0)}\n")
    output.write("\n")

    # Write priority distribution
    output.write("Priority Distribution\n")
    output.write("Priority,Count\n")
    by_priority = analytics_data.get('by_priority', {})
    for priority, count in by_priority.items():
        output.write(f"{priority},{count}\n")

    return output.getvalue()


async def export_analytics_summary_json(
    db: AsyncSession,
    user_id: UUID,
    analytics_data: Dict[str, Any]
) -> str:
    """
    Export analytics summary to JSON format.

    Args:
        db: Database session
        user_id: User ID
        analytics_data: Analytics data dictionary

    Returns:
        JSON string with analytics summary
    """
    export_object = {
        "export_type": "analytics_summary",
        "export_date": datetime.utcnow().isoformat(),
        "user_id": str(user_id),
        "analytics": analytics_data
    }

    return json.dumps(export_object, indent=2)
