"""
Task management routes for the Todo application API.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from ..database import get_session
from ..models import Task, TaskCreate, TaskRead, TaskUpdate, TaskToggleComplete
from ..auth import get_current_user, TokenData

router = APIRouter(prefix="/api/{user_id}", tags=["tasks"])


@router.get("/tasks", response_model=List[TaskRead])
async def list_tasks(
    user_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve all tasks for the specified user.

    Args:
        user_id: The ID of the user whose tasks to retrieve
        current_user: The currently authenticated user
        session: Database session

    Returns:
        List of tasks for the user

    Raises:
        HTTPException: If user is not authorized to access these tasks
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    # Query for tasks belonging to the user
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()

    return tasks


@router.post("/tasks", response_model=TaskRead)
async def create_task(
    user_id: int,
    task: TaskCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the specified user.

    Args:
        user_id: The ID of the user creating the task
        task: Task creation data
        current_user: The currently authenticated user
        session: Database session

    Returns:
        The created task

    Raises:
        HTTPException: If user is not authorized to create tasks for this user
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != user_id:
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
    user_id: int,
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific task for the specified user.

    Args:
        user_id: The ID of the user whose task to retrieve
        task_id: The ID of the task to retrieve
        current_user: The currently authenticated user
        session: Database session

    Returns:
        The requested task

    Raises:
        HTTPException: If task is not found or user is not authorized to access it
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )

    # Query for the specific task belonging to the user
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return db_task


@router.put("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: int,
    task_id: int,
    task_update: TaskUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task for the specified user.

    Args:
        user_id: The ID of the user whose task to update
        task_id: The ID of the task to update
        task_update: Task update data
        current_user: The currently authenticated user
        session: Database session

    Returns:
        The updated task

    Raises:
        HTTPException: If task is not found or user is not authorized to update it
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update these tasks"
        )

    # Query for the specific task belonging to the user
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update task fields if they are provided
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(db_task, field, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task


@router.delete("/tasks/{task_id}")
async def delete_task(
    user_id: int,
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task for the specified user.

    Args:
        user_id: The ID of the user whose task to delete
        task_id: The ID of the task to delete
        current_user: The currently authenticated user
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If task is not found or user is not authorized to delete it
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != user_id:
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

    session.delete(db_task)
    session.commit()

    return {"message": "Task deleted successfully"}


@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    user_id: int,
    task_id: int,
    completion_data: TaskToggleComplete,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a specific task for the specified user.

    Args:
        user_id: The ID of the user whose task to update
        task_id: The ID of the task to update
        completion_data: Completion status data
        current_user: The currently authenticated user
        session: Database session

    Returns:
        The updated task with new completion status

    Raises:
        HTTPException: If task is not found or user is not authorized to update it
    """
    # Verify that the requested user ID matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update these tasks"
        )

    # Query for the specific task belonging to the user
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update the completion status
    db_task.completed = completion_data.completed
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task