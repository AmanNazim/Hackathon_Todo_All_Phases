"""
Task filtering service for advanced filtering and sorting.
"""

from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select, and_, or_
from models import Task, TaskTag


def filter_tasks(
    db: Session,
    user_id: UUID,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    completed: Optional[bool] = None,
    tags: Optional[List[str]] = None,
    due_date_from: Optional[datetime] = None,
    due_date_to: Optional[datetime] = None,
    include_deleted: bool = False,
    sort_by: str = "created_at",
    order: str = "desc",
    page: int = 1,
    limit: int = 20
) -> Tuple[List[Task], int]:
    """
    Filter and sort tasks with pagination.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        status: Optional status filter
        priority: Optional priority filter
        completed: Optional completion status filter
        tags: Optional list of tags to filter by
        due_date_from: Optional start date for due date range
        due_date_to: Optional end date for due date range
        include_deleted: Whether to include soft-deleted tasks
        sort_by: Field to sort by
        order: Sort order (asc or desc)
        page: Page number for pagination
        limit: Items per page

    Returns:
        Tuple of (list of tasks, total count)
    """
    # Build base query
    query = select(Task).where(Task.user_id == user_id)

    # Exclude deleted tasks unless specified
    if not include_deleted:
        query = query.where(Task.deleted == False)

    # Add status filter
    if status:
        query = query.where(Task.status == status)

    # Add priority filter
    if priority:
        query = query.where(Task.priority == priority)

    # Add completion filter
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Add due date range filter
    if due_date_from:
        query = query.where(Task.due_date >= due_date_from)
    if due_date_to:
        query = query.where(Task.due_date <= due_date_to)

    # Add tag filter (requires join with task_tags)
    if tags:
        query = query.join(TaskTag).where(TaskTag.tag.in_(tags))

    # Get total count before pagination
    count_query = select(Task.id).where(Task.user_id == user_id)
    if not include_deleted:
        count_query = count_query.where(Task.deleted == False)
    if status:
        count_query = count_query.where(Task.status == status)
    if priority:
        count_query = count_query.where(Task.priority == priority)
    if completed is not None:
        count_query = count_query.where(Task.completed == completed)
    if due_date_from:
        count_query = count_query.where(Task.due_date >= due_date_from)
    if due_date_to:
        count_query = count_query.where(Task.due_date <= due_date_to)
    if tags:
        count_query = count_query.join(TaskTag).where(TaskTag.tag.in_(tags))

    total_count = len(db.exec(count_query).all())

    # Add sorting
    sort_field = getattr(Task, sort_by, Task.created_at)
    if order.lower() == "asc":
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())

    # Add pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    # Execute query
    result = db.exec(query)
    tasks = result.all()

    return tasks, total_count


def filter_by_status(
    db: Session,
    user_id: UUID,
    status: str,
    include_deleted: bool = False
) -> List[Task]:
    """
    Filter tasks by status.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        status: Status to filter by
        include_deleted: Whether to include soft-deleted tasks

    Returns:
        List of tasks with specified status
    """
    query = select(Task).where(
        and_(
            Task.user_id == user_id,
            Task.status == status
        )
    )

    if not include_deleted:
        query = query.where(Task.deleted == False)

    result = db.exec(query)
    return result.all()


def filter_by_priority(
    db: Session,
    user_id: UUID,
    priority: str,
    include_deleted: bool = False
) -> List[Task]:
    """
    Filter tasks by priority.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        priority: Priority to filter by
        include_deleted: Whether to include soft-deleted tasks

    Returns:
        List of tasks with specified priority
    """
    query = select(Task).where(
        and_(
            Task.user_id == user_id,
            Task.priority == priority
        )
    )

    if not include_deleted:
        query = query.where(Task.deleted == False)

    result = db.exec(query)
    return result.all()


def filter_by_date_range(
    db: Session,
    user_id: UUID,
    start_date: datetime,
    end_date: datetime,
    include_deleted: bool = False
) -> List[Task]:
    """
    Filter tasks by due date range.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        start_date: Start of date range
        end_date: End of date range
        include_deleted: Whether to include soft-deleted tasks

    Returns:
        List of tasks within date range
    """
    query = select(Task).where(
        and_(
            Task.user_id == user_id,
            Task.due_date >= start_date,
            Task.due_date <= end_date
        )
    )

    if not include_deleted:
        query = query.where(Task.deleted == False)

    result = db.exec(query)
    return result.all()


def get_overdue_tasks(
    db: Session,
    user_id: UUID,
    include_deleted: bool = False
) -> List[Task]:
    """
    Get all overdue tasks for a user.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        include_deleted: Whether to include soft-deleted tasks

    Returns:
        List of overdue tasks
    """
    now = datetime.utcnow()
    query = select(Task).where(
        and_(
            Task.user_id == user_id,
            Task.completed == False,
            Task.due_date < now,
            Task.due_date.isnot(None)
        )
    )

    if not include_deleted:
        query = query.where(Task.deleted == False)

    result = db.exec(query)
    return result.all()
