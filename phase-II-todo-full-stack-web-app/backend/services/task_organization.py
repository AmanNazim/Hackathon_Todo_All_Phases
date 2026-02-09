"""
Task organization service for tag-based operations.
"""
from typing import List, Dict
from sqlmodel import Session, select, func
from models import Task, TaskTag


def get_tasks_by_tag(session: Session, user_id: str, tag: str) -> List[Task]:
    """
    Get all tasks for a user with a specific tag.

    Args:
        session: Database session
        user_id: User ID
        tag: Tag name

    Returns:
        List of tasks with the specified tag
    """
    statement = (
        select(Task)
        .join(TaskTag)
        .where(
            Task.user_id == user_id,
            Task.deleted == False,
            TaskTag.tag == tag
        )
        .order_by(Task.created_at.desc())
    )

    tasks = session.exec(statement).all()
    return list(tasks)


def get_tag_statistics(session: Session, user_id: str) -> Dict[str, int]:
    """
    Get statistics about tag usage for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Dictionary mapping tag names to usage counts
    """
    statement = (
        select(TaskTag.tag, func.count(TaskTag.task_id).label('count'))
        .join(Task)
        .where(
            Task.user_id == user_id,
            Task.deleted == False
        )
        .group_by(TaskTag.tag)
        .order_by(func.count(TaskTag.task_id).desc())
    )

    results = session.exec(statement).all()
    return {tag: count for tag, count in results}


def get_popular_tags(session: Session, user_id: str, limit: int = 10) -> List[str]:
    """
    Get most popular tags for a user.

    Args:
        session: Database session
        user_id: User ID
        limit: Maximum number of tags to return

    Returns:
        List of popular tag names
    """
    statement = (
        select(TaskTag.tag, func.count(TaskTag.task_id).label('count'))
        .join(Task)
        .where(
            Task.user_id == user_id,
            Task.deleted == False
        )
        .group_by(TaskTag.tag)
        .order_by(func.count(TaskTag.task_id).desc())
        .limit(limit)
    )

    results = session.exec(statement).all()
    return [tag for tag, _ in results]


def get_all_user_tags(session: Session, user_id: str) -> List[str]:
    """
    Get all unique tags used by a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        List of unique tag names
    """
    statement = (
        select(TaskTag.tag)
        .join(Task)
        .where(
            Task.user_id == user_id,
            Task.deleted == False
        )
        .distinct()
        .order_by(TaskTag.tag)
    )

    tags = session.exec(statement).all()
    return list(tags)
