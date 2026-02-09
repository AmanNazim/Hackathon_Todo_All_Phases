"""
Task management routes for the Todo application API.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from database import get_session
from models import (
    Task, TaskCreate, TaskRead, TaskUpdate, TaskToggleComplete,
    TaskTag, TagRead, TaskHistory, TaskHistoryRead,
    BatchOperationRequest, BatchOperationResponse
)
from auth import get_current_user, TokenData
from services.task_workflow import validate_status_transition, enforce_status_transition
from services.task_filter import filter_tasks, get_overdue_tasks
from services.task_search import search_tasks
from services.task_batch import (
    batch_update_status, batch_update_priority, batch_delete_tasks,
    batch_add_tags, batch_remove_tags
)
from services.task_history import get_task_history, track_task_update

router = APIRouter(prefix="/api/v1/users/{user_id}", tags=["tasks"])


@router.get("/tasks")
async def list_tasks(
    user_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
    completed: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    sort: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Retrieve tasks for the specified user with filtering, search, and pagination.

    Args:
        user_id: The UUID of the user whose tasks to retrieve
        current_user: The currently authenticated user
        session: Database session
        status_filter: Filter by status
        priority: Filter by priority
        completed: Filter by completion status
        search: Search query for title/description
        tags: Filter by tags
        sort: Sort field
        order: Sort order (asc/desc)
        page: Page number
        limit: Items per page

    Returns:
        Dictionary with tasks and pagination info

    Raises:
        HTTPException: If user is not authorized to access these tasks
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    # Use search if provided
    if search:
        tasks = search_tasks(session, user_id, search, include_deleted=False)
        total = len(tasks)

        # Apply pagination manually for search results
        start = (page - 1) * limit
        end = start + limit
        tasks = tasks[start:end]
    else:
        # Use filter service
        tasks, total = filter_tasks(
            db=session,
            user_id=user_id,
            status=status_filter,
            priority=priority,
            completed=completed,
            tags=tags,
            sort_by=sort,
            order=order,
            page=page,
            limit=limit
        )

    return {
        "tasks": [TaskRead.from_orm(task) for task in tasks],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: UUID,
    task: TaskCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the specified user.

    Args:
        user_id: The UUID of the user creating the task
        task: Task creation data
        current_user: The currently authenticated user
        session: Database session

    Returns:
        The created task

    Raises:
        HTTPException: If user is not authorized to create tasks for this user
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks for this user"
        )

    # Create the new task
    db_task = Task.model_validate(task)
    db_task.user_id = user_id

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    user_id: UUID,
    task_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific task for the specified user.

    Args:
        user_id: The UUID of the user whose task to retrieve
        task_id: The UUID of the task to retrieve
        current_user: The currently authenticated user
        session: Database session

    Returns:
        The requested task

    Raises:
        HTTPException: If task is not found or user is not authorized to access it
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    # Query for the specific task belonging to the user (exclude deleted)
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.deleted == False
    )
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return db_task


@router.put("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: UUID,
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task for the specified user.

    Args:
        user_id: The UUID of the user whose task to update
        task_id: The UUID of the task to update
        task_update: Task update data
        current_user: The currently authenticated user
        session: Database session

    Returns:
        The updated task

    Raises:
        HTTPException: If task is not found or user is not authorized to update it
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update these tasks"
        )

    # Query for the specific task belonging to the user
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.deleted == False
    )
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Store old values for history tracking
    old_data = {
        "title": db_task.title,
        "description": db_task.description,
        "status": db_task.status,
        "priority": db_task.priority,
        "completed": db_task.completed,
        "due_date": db_task.due_date
    }

    # Validate status transition if status is being updated
    update_dict = task_update.dict(exclude_unset=True)
    if "status" in update_dict and update_dict["status"] != db_task.status:
        enforce_status_transition(db_task.status, update_dict["status"])

    # Update task fields if they are provided
    for field, value in update_dict.items():
        setattr(db_task, field, value)

    # Auto-complete if status is 'done'
    if "status" in update_dict and update_dict["status"] == "done":
        if not db_task.completed:
            db_task.completed = True
            db_task.completed_at = datetime.utcnow()

    db_task.updated_at = datetime.utcnow()
    session.add(db_task)
    session.commit()

    # Track changes in history
    track_task_update(session, db_task, user_id, old_data, update_dict)

    session.refresh(db_task)
    return db_task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    user_id: UUID,
    task_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
    hard_delete: bool = Query(False, description="Permanently delete task")
):
    """
    Delete a specific task for the specified user (soft delete by default).

    Args:
        user_id: The UUID of the user whose task to delete
        task_id: The UUID of the task to delete
        current_user: The currently authenticated user
        session: Database session
        hard_delete: If True, permanently delete; if False, soft delete

    Returns:
        Success message

    Raises:
        HTTPException: If task is not found or user is not authorized to delete it
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete these tasks"
        )

    # Query for the specific task belonging to the user
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if hard_delete:
        # Permanently delete
        session.delete(db_task)
        message = "Task permanently deleted"
    else:
        # Soft delete
        db_task.deleted = True
        db_task.deleted_at = datetime.utcnow()
        session.add(db_task)
        message = "Task deleted successfully (can be recovered within 30 days)"

    session.commit()
    return {"message": message}


@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    user_id: UUID,
    task_id: UUID,
    completion_data: TaskToggleComplete,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a specific task for the specified user.

    Args:
        user_id: The UUID of the user whose task to update
        task_id: The UUID of the task to update
        completion_data: Completion status data
        current_user: The currently authenticated user
        session: Database session

    Returns:
        The updated task with new completion status

    Raises:
        HTTPException: If task is not found or user is not authorized to update it
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update these tasks"
        )

    # Query for the specific task belonging to the user
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.deleted == False
    )
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update the completion status
    db_task.completed = completion_data.completed

    # Set completed_at timestamp
    if completion_data.completed:
        db_task.completed_at = datetime.utcnow()
        # Auto-update status to 'done' if not already
        if db_task.status != "done":
            db_task.status = "done"
    else:
        db_task.completed_at = None
        # Revert status if uncompleting
        if db_task.status == "done":
            db_task.status = "todo"

    db_task.updated_at = datetime.utcnow()
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task

# New endpoints to add to routes/tasks.py

@router.get("/tasks/statistics")
async def get_task_statistics(
    user_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get task statistics for the specified user.

    Args:
        user_id: The UUID of the user
        current_user: The currently authenticated user
        session: Database session

    Returns:
        Dictionary with task statistics

    Raises:
        HTTPException: If user is not authorized
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these statistics"
        )

    # Get all tasks (excluding deleted)
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.deleted == False
    )
    all_tasks = session.exec(statement).all()

    # Calculate statistics
    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for task in all_tasks if task.completed)
    pending_tasks = total_tasks - completed_tasks

    # Get overdue tasks
    overdue_tasks = get_overdue_tasks(session, user_id, include_deleted=False)
    overdue_count = len(overdue_tasks)

    # Count by priority
    by_priority = {
        "low": sum(1 for task in all_tasks if task.priority == "low"),
        "medium": sum(1 for task in all_tasks if task.priority == "medium"),
        "high": sum(1 for task in all_tasks if task.priority == "high"),
        "urgent": sum(1 for task in all_tasks if task.priority == "urgent")
    }

    # Count by status
    by_status = {
        "todo": sum(1 for task in all_tasks if task.status == "todo"),
        "in_progress": sum(1 for task in all_tasks if task.status == "in_progress"),
        "review": sum(1 for task in all_tasks if task.status == "review"),
        "done": sum(1 for task in all_tasks if task.status == "done"),
        "blocked": sum(1 for task in all_tasks if task.status == "blocked")
    }

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_count,
        "by_priority": by_priority,
        "by_status": by_status
    }


@router.post("/tasks/batch", response_model=BatchOperationResponse)
async def batch_operations(
    user_id: UUID,
    batch_request: BatchOperationRequest,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Perform batch operations on multiple tasks.

    Args:
        user_id: The UUID of the user
        batch_request: Batch operation request data
        current_user: The currently authenticated user
        session: Database session

    Returns:
        Batch operation response with counts and errors

    Raises:
        HTTPException: If user is not authorized or operation is invalid
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform batch operations"
        )

    operation = batch_request.operation
    task_ids = batch_request.task_ids
    data = batch_request.data or {}

    # Perform the requested operation
    if operation == "update_status":
        new_status = data.get("status")
        if not new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status is required for update_status operation"
            )
        updated, failed, errors = batch_update_status(session, user_id, task_ids, new_status)

    elif operation == "update_priority":
        new_priority = data.get("priority")
        if not new_priority:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Priority is required for update_priority operation"
            )
        updated, failed, errors = batch_update_priority(session, user_id, task_ids, new_priority)

    elif operation == "delete":
        hard_delete = data.get("hard_delete", False)
        updated, failed, errors = batch_delete_tasks(session, user_id, task_ids, hard_delete)

    elif operation == "add_tags":
        tags = data.get("tags", [])
        if not tags:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tags are required for add_tags operation"
            )
        updated, failed, errors = batch_add_tags(session, user_id, task_ids, tags)

    elif operation == "remove_tags":
        tags = data.get("tags", [])
        if not tags:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tags are required for remove_tags operation"
            )
        updated, failed, errors = batch_remove_tags(session, user_id, task_ids, tags)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation: {operation}. Valid operations: update_status, update_priority, delete, add_tags, remove_tags"
        )

    return BatchOperationResponse(
        updated=updated,
        failed=failed,
        errors=errors if errors else None
    )


@router.post("/tasks/{task_id}/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def add_tag_to_task(
    user_id: UUID,
    task_id: UUID,
    tag: str = Query(..., min_length=1, max_length=50),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Add a tag to a specific task.

    Args:
        user_id: The UUID of the user
        task_id: The UUID of the task
        tag: Tag to add
        current_user: The currently authenticated user
        session: Database session

    Returns:
        Created tag

    Raises:
        HTTPException: If task is not found or user is not authorized
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify these tasks"
        )

    # Verify task exists and belongs to user
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.deleted == False
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Check if tag already exists
    existing_tag = session.exec(
        select(TaskTag).where(
            TaskTag.task_id == task_id,
            TaskTag.tag == tag
        )
    ).first()

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already exists on this task"
        )

    # Create new tag
    new_tag = TaskTag(task_id=task_id, tag=tag)
    session.add(new_tag)

    # Update task timestamp
    task.updated_at = datetime.utcnow()
    session.add(task)

    session.commit()
    session.refresh(new_tag)

    return new_tag


@router.delete("/tasks/{task_id}/tags/{tag}", status_code=status.HTTP_200_OK)
async def remove_tag_from_task(
    user_id: UUID,
    task_id: UUID,
    tag: str,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Remove a tag from a specific task.

    Args:
        user_id: The UUID of the user
        task_id: The UUID of the task
        tag: Tag to remove
        current_user: The currently authenticated user
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If task or tag is not found or user is not authorized
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify these tasks"
        )

    # Verify task exists and belongs to user
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.deleted == False
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Find and delete tag
    existing_tag = session.exec(
        select(TaskTag).where(
            TaskTag.task_id == task_id,
            TaskTag.tag == tag
        )
    ).first()

    if not existing_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found on this task"
        )

    session.delete(existing_tag)

    # Update task timestamp
    task.updated_at = datetime.utcnow()
    session.add(task)

    session.commit()

    return {"message": "Tag removed successfully"}


@router.get("/tasks/{task_id}/tags", response_model=List[TagRead])
async def get_task_tags(
    user_id: UUID,
    task_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all tags for a specific task.

    Args:
        user_id: The UUID of the user
        task_id: The UUID of the task
        current_user: The currently authenticated user
        session: Database session

    Returns:
        List of tags

    Raises:
        HTTPException: If task is not found or user is not authorized
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    # Verify task exists and belongs to user
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.deleted == False
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Get all tags for the task
    tags_statement = select(TaskTag).where(TaskTag.task_id == task_id)
    tags = session.exec(tags_statement).all()

    return tags


@router.get("/tasks/{task_id}/history", response_model=List[TaskHistoryRead])
async def get_task_history_endpoint(
    user_id: UUID,
    task_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Get change history for a specific task.

    Args:
        user_id: The UUID of the user
        task_id: The UUID of the task
        current_user: The currently authenticated user
        session: Database session
        limit: Maximum number of history entries to return

    Returns:
        List of history entries

    Raises:
        HTTPException: If task is not found or user is not authorized
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access task history"
        )

    # Get history entries
    history = get_task_history(session, task_id, user_id, limit)

    return history
