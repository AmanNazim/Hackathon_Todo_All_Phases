"""
Database utility functions for common operations.
"""

from typing import Optional, List
from uuid import UUID
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Task, UserCreate, TaskCreate, TaskUpdate
from datetime import datetime
import bcrypt


# User Operations

async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user with hashed password."""
    # Hash the password
    password_hash = bcrypt.hashpw(
        user_data.password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    # Create user instance
    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password_hash=password_hash,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get a user by ID."""
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email."""
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


# Task Operations

async def create_task(session: AsyncSession, user_id: UUID, task_data: TaskCreate) -> Task:
    """Create a new task for a user."""
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
        priority=task_data.priority,
        due_date=task_data.due_date,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_task_by_id(session: AsyncSession, task_id: UUID, user_id: UUID) -> Optional[Task]:
    """Get a task by ID, ensuring it belongs to the user."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_tasks(
    session: AsyncSession,
    user_id: UUID,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """Get all tasks for a user with optional filtering."""
    statement = select(Task).where(Task.user_id == user_id)

    # Apply filters
    if completed is not None:
        statement = statement.where(Task.completed == completed)

    if priority is not None:
        statement = statement.where(Task.priority == priority)

    # Apply pagination
    statement = statement.offset(skip).limit(limit)

    # Order by created_at descending
    statement = statement.order_by(Task.created_at.desc())

    result = await session.execute(statement)
    return result.scalars().all()


async def update_task(
    session: AsyncSession,
    task_id: UUID,
    user_id: UUID,
    task_data: TaskUpdate
) -> Optional[Task]:
    """Update a task, ensuring it belongs to the user."""
    task = await get_task_by_id(session, task_id, user_id)

    if not task:
        return None

    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task_id: UUID, user_id: UUID) -> bool:
    """Delete a task, ensuring it belongs to the user."""
    task = await get_task_by_id(session, task_id, user_id)

    if not task:
        return False

    await session.delete(task)
    await session.commit()
    return True


async def toggle_task_completion(
    session: AsyncSession,
    task_id: UUID,
    user_id: UUID,
    completed: bool
) -> Optional[Task]:
    """Toggle task completion status."""
    task = await get_task_by_id(session, task_id, user_id)

    if not task:
        return None

    task.completed = completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_task_statistics(session: AsyncSession, user_id: UUID) -> dict:
    """Get task statistics for a user."""
    # Get all tasks
    all_tasks = await get_user_tasks(session, user_id, limit=10000)

    # Calculate statistics
    total = len(all_tasks)
    completed = sum(1 for task in all_tasks if task.completed)
    pending = total - completed

    # Count by priority
    priority_counts = {
        'low': sum(1 for task in all_tasks if task.priority == 'low'),
        'medium': sum(1 for task in all_tasks if task.priority == 'medium'),
        'high': sum(1 for task in all_tasks if task.priority == 'high'),
        'urgent': sum(1 for task in all_tasks if task.priority == 'urgent'),
    }

    # Count overdue tasks
    now = datetime.utcnow()
    overdue = sum(
        1 for task in all_tasks
        if not task.completed and task.due_date and task.due_date < now
    )

    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'overdue': overdue,
        'by_priority': priority_counts,
    }