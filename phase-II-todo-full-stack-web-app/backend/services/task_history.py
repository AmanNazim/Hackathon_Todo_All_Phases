"""
Task history tracking service for audit trail.
"""

from typing import List, Dict, Optional, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlmodel import Session, select
from models import Task, TaskHistory


def track_change(
    db: Session,
    task_id: UUID,
    user_id: UUID,
    change_type: str,
    old_value: Optional[Dict[str, Any]] = None,
    new_value: Optional[Dict[str, Any]] = None
) -> TaskHistory:
    """
    Track a change to a task.

    Args:
        db: Database session
        task_id: Task ID
        user_id: User ID who made the change
        change_type: Type of change (e.g., 'status_change', 'priority_change')
        old_value: Previous value(s)
        new_value: New value(s)

    Returns:
        Created TaskHistory entry
    """
    history_entry = TaskHistory(
        task_id=task_id,
        user_id=user_id,
        change_type=change_type,
        old_value=old_value,
        new_value=new_value
    )

    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)

    return history_entry


def create_history_entry(
    db: Session,
    task: Task,
    user_id: UUID,
    change_type: str,
    field_name: str,
    old_value: Any,
    new_value: Any
) -> TaskHistory:
    """
    Create a history entry for a specific field change.

    Args:
        db: Database session
        task: Task object
        user_id: User ID who made the change
        change_type: Type of change
        field_name: Name of the field that changed
        old_value: Previous value
        new_value: New value

    Returns:
        Created TaskHistory entry
    """
    return track_change(
        db=db,
        task_id=task.id,
        user_id=user_id,
        change_type=change_type,
        old_value={field_name: old_value},
        new_value={field_name: new_value}
    )


def get_task_history(
    db: Session,
    task_id: UUID,
    user_id: UUID,
    limit: int = 50
) -> List[TaskHistory]:
    """
    Get history for a specific task.

    Args:
        db: Database session
        task_id: Task ID
        user_id: User ID (for authorization)
        limit: Maximum number of history entries to return

    Returns:
        List of TaskHistory entries
    """
    # Verify task belongs to user
    task = db.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()

    if not task:
        return []

    # Get history entries
    statement = select(TaskHistory).where(
        TaskHistory.task_id == task_id
    ).order_by(
        TaskHistory.created_at.desc()
    ).limit(limit)

    result = db.exec(statement)
    return result.all()


def compare_changes(
    history_entry: TaskHistory
) -> Dict[str, Any]:
    """
    Compare old and new values in a history entry.

    Args:
        history_entry: TaskHistory entry

    Returns:
        Dictionary with comparison details
    """
    comparison = {
        "change_type": history_entry.change_type,
        "timestamp": history_entry.created_at,
        "changes": []
    }

    if history_entry.old_value and history_entry.new_value:
        # Compare each field
        old_keys = set(history_entry.old_value.keys())
        new_keys = set(history_entry.new_value.keys())
        all_keys = old_keys.union(new_keys)

        for key in all_keys:
            old_val = history_entry.old_value.get(key)
            new_val = history_entry.new_value.get(key)

            if old_val != new_val:
                comparison["changes"].append({
                    "field": key,
                    "old_value": old_val,
                    "new_value": new_val
                })

    return comparison


def get_diff(
    db: Session,
    task_id: UUID,
    user_id: UUID,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Get differences in task state over time.

    Args:
        db: Database session
        task_id: Task ID
        user_id: User ID (for authorization)
        from_date: Start date for diff
        to_date: End date for diff

    Returns:
        List of change comparisons
    """
    # Verify task belongs to user
    task = db.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()

    if not task:
        return []

    # Build query
    query = select(TaskHistory).where(TaskHistory.task_id == task_id)

    if from_date:
        query = query.where(TaskHistory.created_at >= from_date)
    if to_date:
        query = query.where(TaskHistory.created_at <= to_date)

    query = query.order_by(TaskHistory.created_at.asc())

    # Get history entries
    result = db.exec(query)
    history_entries = result.all()

    # Compare changes
    diffs = []
    for entry in history_entries:
        diffs.append(compare_changes(entry))

    return diffs


def track_task_update(
    db: Session,
    task: Task,
    user_id: UUID,
    old_data: Dict[str, Any],
    new_data: Dict[str, Any]
) -> List[TaskHistory]:
    """
    Track multiple field changes in a task update.

    Args:
        db: Database session
        task: Task object
        user_id: User ID who made the change
        old_data: Dictionary of old field values
        new_data: Dictionary of new field values

    Returns:
        List of created TaskHistory entries
    """
    history_entries = []

    # Track each changed field
    for field, new_value in new_data.items():
        old_value = old_data.get(field)

        if old_value != new_value:
            entry = create_history_entry(
                db=db,
                task=task,
                user_id=user_id,
                change_type=f"{field}_change",
                field_name=field,
                old_value=old_value,
                new_value=new_value
            )
            history_entries.append(entry)

    return history_entries


def cleanup_old_history(
    db: Session,
    days: int = 90
) -> int:
    """
    Clean up history entries older than specified days.

    Args:
        db: Database session
        days: Number of days to retain history

    Returns:
        Number of entries deleted
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    statement = select(TaskHistory).where(
        TaskHistory.created_at < cutoff_date
    )

    old_entries = db.exec(statement).all()
    count = len(old_entries)

    for entry in old_entries:
        db.delete(entry)

    db.commit()
    return count
