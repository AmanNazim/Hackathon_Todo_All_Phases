"""
Task search service for full-text search functionality.
"""

from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select, or_, and_, func
from models import Task


def search_tasks(
    db: Session,
    user_id: UUID,
    search_query: str,
    include_deleted: bool = False
) -> List[Task]:
    """
    Search tasks using full-text search on title and description.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        search_query: Search query string
        include_deleted: Whether to include soft-deleted tasks

    Returns:
        List of matching tasks
    """
    # Build base query
    query = select(Task).where(Task.user_id == user_id)

    # Exclude deleted tasks unless specified
    if not include_deleted:
        query = query.where(Task.deleted == False)

    # Add search conditions
    search_pattern = f"%{search_query}%"
    query = query.where(
        or_(
            Task.title.ilike(search_pattern),
            Task.description.ilike(search_pattern)
        )
    )

    # Execute query
    result = db.exec(query)
    return result.all()


def search_tasks_advanced(
    db: Session,
    user_id: UUID,
    search_query: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    completed: Optional[bool] = None,
    tags: Optional[List[str]] = None,
    include_deleted: bool = False
) -> List[Task]:
    """
    Advanced search with multiple filters.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        search_query: Optional search query string
        status: Optional status filter
        priority: Optional priority filter
        completed: Optional completion status filter
        tags: Optional list of tags to filter by
        include_deleted: Whether to include soft-deleted tasks

    Returns:
        List of matching tasks
    """
    # Build base query
    query = select(Task).where(Task.user_id == user_id)

    # Exclude deleted tasks unless specified
    if not include_deleted:
        query = query.where(Task.deleted == False)

    # Add search condition
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.where(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )

    # Add status filter
    if status:
        query = query.where(Task.status == status)

    # Add priority filter
    if priority:
        query = query.where(Task.priority == priority)

    # Add completion filter
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Add tag filter (requires join with task_tags)
    if tags:
        from models import TaskTag
        query = query.join(TaskTag).where(TaskTag.tag.in_(tags))

    # Execute query
    result = db.exec(query)
    return result.all()


def count_search_results(
    db: Session,
    user_id: UUID,
    search_query: str,
    include_deleted: bool = False
) -> int:
    """
    Count number of search results without fetching all data.

    Args:
        db: Database session
        user_id: User ID to filter tasks
        search_query: Search query string
        include_deleted: Whether to include soft-deleted tasks

    Returns:
        Count of matching tasks
    """
    # Build base query
    query = select(func.count(Task.id)).where(Task.user_id == user_id)

    # Exclude deleted tasks unless specified
    if not include_deleted:
        query = query.where(Task.deleted == False)

    # Add search conditions
    search_pattern = f"%{search_query}%"
    query = query.where(
        or_(
            Task.title.ilike(search_pattern),
            Task.description.ilike(search_pattern)
        )
    )

    # Execute query
    result = db.exec(query)
    return result.one()
