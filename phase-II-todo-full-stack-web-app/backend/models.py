"""
Database models for the Todo application using SQLModel.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel


class UserBase(SQLModel):
    """Base model for user with common attributes."""
    email: str = Field(unique=True, nullable=False)


class User(UserBase, table=True):
    """User model representing application users."""
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: list["Task"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """Model for creating new users."""
    password: str


class UserRead(UserBase):
    """Model for reading user data."""
    id: int
    created_at: datetime
    updated_at: datetime


class UserUpdate(SQLModel):
    """Model for updating user data."""
    email: Optional[str] = None
    password: Optional[str] = None


class TaskBase(SQLModel):
    """Base model for task with common attributes."""
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    """Task model representing user tasks."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: Optional[User] = Relationship(back_populates="tasks")


class TaskCreate(TaskBase):
    """Model for creating new tasks."""
    pass


class TaskRead(TaskBase):
    """Model for reading task data."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    """Model for updating task data."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskToggleComplete(BaseModel):
    """Model for toggling task completion status."""
    completed: bool