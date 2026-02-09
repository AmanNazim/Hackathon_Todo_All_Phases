"""
Batch operations service for performing bulk actions on tasks.
"""

from typing import List, Dict, Optional, Tuple
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
from models import Task, TaskTag
from services.task_workflow import validate_status_transition


def batch_update_status(
    db: Session,
    user_id: UUID,
    task_ids: List[UUID],
    new_status: str
) -> Tuple[int, int, List[Dict]]:
    """
    Update status for multiple tasks.

    Args:
        db: Database session
        user_id: User ID (for authorization)
        task_ids: List of task IDs to update
        new_status: New status to set

    Returns:
        Tuple of (updated_count, failed_count, error_list)
    """
    updated = 0
    failed = 0
    errors = []

    for task_id in task_ids:
        try:
            # Get task
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted == False
            )
            task = db.exec(statement).first()

            if not task:
                failed += 1
                errors.append({
                    "task_id": str(task_id),
                    "error": "Task not found or access denied"
                })
                continue

            # Validate status transition
            if not validate_status_transition(task.status, new_status):
                failed += 1
                errors.append({
                    "task_id": str(task_id),
                    "error": f"Invalid status transition from '{task.status}' to '{new_status}'"
                })
                continue

            # Update status
            task.status = new_status
            task.updated_at = datetime.utcnow()

            # Auto-complete if status is 'done'
            if new_status == "done" and not task.completed:
                task.completed = True
                task.completed_at = datetime.utcnow()

            db.add(task)
            updated += 1

        except Exception as e:
            failed += 1
            errors.append({
                "task_id": str(task_id),
                "error": str(e)
            })

    db.commit()
    return updated, failed, errors


def batch_update_priority(
    db: Session,
    user_id: UUID,
    task_ids: List[UUID],
    new_priority: str
) -> Tuple[int, int, List[Dict]]:
    """
    Update priority for multiple tasks.

    Args:
        db: Database session
        user_id: User ID (for authorization)
        task_ids: List of task IDs to update
        new_priority: New priority to set

    Returns:
        Tuple of (updated_count, failed_count, error_list)
    """
    updated = 0
    failed = 0
    errors = []

    valid_priorities = ["low", "medium", "high", "urgent"]
    if new_priority not in valid_priorities:
        return 0, len(task_ids), [{
            "task_id": "all",
            "error": f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
        }]

    for task_id in task_ids:
        try:
            # Get task
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted == False
            )
            task = db.exec(statement).first()

            if not task:
                failed += 1
                errors.append({
                    "task_id": str(task_id),
                    "error": "Task not found or access denied"
                })
                continue

            # Update priority
            task.priority = new_priority
            task.updated_at = datetime.utcnow()
            db.add(task)
            updated += 1

        except Exception as e:
            failed += 1
            errors.append({
                "task_id": str(task_id),
                "error": str(e)
            })

    db.commit()
    return updated, failed, errors


def batch_delete_tasks(
    db: Session,
    user_id: UUID,
    task_ids: List[UUID],
    hard_delete: bool = False
) -> Tuple[int, int, List[Dict]]:
    """
    Delete multiple tasks (soft delete by default).

    Args:
        db: Database session
        user_id: User ID (for authorization)
        task_ids: List of task IDs to delete
        hard_delete: If True, permanently delete; if False, soft delete

    Returns:
        Tuple of (deleted_count, failed_count, error_list)
    """
    deleted = 0
    failed = 0
    errors = []

    for task_id in task_ids:
        try:
            # Get task
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            task = db.exec(statement).first()

            if not task:
                failed += 1
                errors.append({
                    "task_id": str(task_id),
                    "error": "Task not found or access denied"
                })
                continue

            if hard_delete:
                # Permanently delete
                db.delete(task)
            else:
                # Soft delete
                task.deleted = True
                task.deleted_at = datetime.utcnow()
                db.add(task)

            deleted += 1

        except Exception as e:
            failed += 1
            errors.append({
                "task_id": str(task_id),
                "error": str(e)
            })

    db.commit()
    return deleted, failed, errors


def batch_add_tags(
    db: Session,
    user_id: UUID,
    task_ids: List[UUID],
    tags: List[str]
) -> Tuple[int, int, List[Dict]]:
    """
    Add tags to multiple tasks.

    Args:
        db: Database session
        user_id: User ID (for authorization)
        task_ids: List of task IDs to add tags to
        tags: List of tags to add

    Returns:
        Tuple of (updated_count, failed_count, error_list)
    """
    updated = 0
    failed = 0
    errors = []

    for task_id in task_ids:
        try:
            # Get task
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted == False
            )
            task = db.exec(statement).first()

            if not task:
                failed += 1
                errors.append({
                    "task_id": str(task_id),
                    "error": "Task not found or access denied"
                })
                continue

            # Add tags
            for tag in tags:
                # Check if tag already exists
                existing_tag = db.exec(
                    select(TaskTag).where(
                        TaskTag.task_id == task_id,
                        TaskTag.tag == tag
                    )
                ).first()

                if not existing_tag:
                    new_tag = TaskTag(task_id=task_id, tag=tag)
                    db.add(new_tag)

            task.updated_at = datetime.utcnow()
            db.add(task)
            updated += 1

        except Exception as e:
            failed += 1
            errors.append({
                "task_id": str(task_id),
                "error": str(e)
            })

    db.commit()
    return updated, failed, errors


def batch_remove_tags(
    db: Session,
    user_id: UUID,
    task_ids: List[UUID],
    tags: List[str]
) -> Tuple[int, int, List[Dict]]:
    """
    Remove tags from multiple tasks.

    Args:
        db: Database session
        user_id: User ID (for authorization)
        task_ids: List of task IDs to remove tags from
        tags: List of tags to remove

    Returns:
        Tuple of (updated_count, failed_count, error_list)
    """
    updated = 0
    failed = 0
    errors = []

    for task_id in task_ids:
        try:
            # Get task
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.deleted == False
            )
            task = db.exec(statement).first()

            if not task:
                failed += 1
                errors.append({
                    "task_id": str(task_id),
                    "error": "Task not found or access denied"
                })
                continue

            # Remove tags
            for tag in tags:
                existing_tag = db.exec(
                    select(TaskTag).where(
                        TaskTag.task_id == task_id,
                        TaskTag.tag == tag
                    )
                ).first()

                if existing_tag:
                    db.delete(existing_tag)

            task.updated_at = datetime.utcnow()
            db.add(task)
            updated += 1

        except Exception as e:
            failed += 1
            errors.append({
                "task_id": str(task_id),
                "error": str(e)
            })

    db.commit()
    return updated, failed, errors


def handle_batch_errors(errors: List[Dict]) -> Dict:
    """
    Format batch operation errors for response.

    Args:
        errors: List of error dictionaries

    Returns:
        Formatted error response
    """
    return {
        "error_count": len(errors),
        "errors": errors
    }
