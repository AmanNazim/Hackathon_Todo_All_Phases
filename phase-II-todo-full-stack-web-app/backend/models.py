"""
Database models for the Todo application using SQLModel.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from pydantic import BaseModel, EmailStr


class UserBase(SQLModel):
    """Base model for user with common attributes."""
    email: EmailStr = Field(unique=True, nullable=False, index=True)
    first_name: str = Field(max_length=100, nullable=False)
    last_name: str = Field(max_length=100, nullable=False)
    display_name: Optional[str] = Field(default=None, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    avatar_thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True, nullable=False)
    email_verified: bool = Field(default=False, nullable=False)


class User(UserBase, table=True):
    """User model representing application users."""
    __tablename__ = "users"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    password_hash: str = Field(nullable=False)
    last_login_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class UserCreate(BaseModel):
    """Model for creating new users."""
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class UserRead(UserBase):
    """Model for reading user data."""
    id: UUID
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class ProfileRead(BaseModel):
    """Model for reading user profile data."""
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    avatar_thumbnail_url: Optional[str]
    email_verified: bool
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    """Model for updating user profile data."""
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)


class UserUpdate(SQLModel):
    """Model for updating user data."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class TaskBase(SQLModel):
    """Base model for task with common attributes."""
    title: str = Field(min_length=1, max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False, index=True)
    priority: str = Field(
        default="medium",
        nullable=False,
        regex="^(low|medium|high|urgent)$",
        index=True
    )
    status: str = Field(
        default="todo",
        nullable=False,
        regex="^(todo|in_progress|review|done|blocked)$",
        index=True
    )
    due_date: Optional[datetime] = Field(default=None, index=True)
    completed_at: Optional[datetime] = Field(default=None)


class Task(TaskBase, table=True):
    """Task model representing user tasks."""
    __tablename__ = "tasks"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    deleted: bool = Field(default=False, nullable=False, index=True)
    deleted_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    # Relationship to user
    user: Optional[User] = Relationship(back_populates="tasks")
    # Relationship to tags
    tags: List["TaskTag"] = Relationship(back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class TaskCreate(TaskBase):
    """Model for creating new tasks."""
    pass


class TaskRead(TaskBase):
    """Model for reading task data."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    """Model for updating task data."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[str] = Field(default=None, regex="^(low|medium|high|urgent)$")
    status: Optional[str] = Field(default=None, regex="^(todo|in_progress|review|done|blocked)$")
    due_date: Optional[datetime] = None


class TaskToggleComplete(BaseModel):
    """Model for toggling task completion status."""
    completed: bool


class PasswordResetToken(SQLModel, table=True):
    """Password reset token model for password recovery."""
    __tablename__ = "password_reset_tokens"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    token_hash: str = Field(nullable=False)
    expires_at: datetime = Field(nullable=False, index=True)
    used: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class EmailVerificationToken(SQLModel, table=True):
    """Email verification token model."""
    __tablename__ = "email_verification_tokens"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    token_hash: str = Field(nullable=False)
    expires_at: datetime = Field(nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class DailyAnalytics(SQLModel, table=True):
    """Daily analytics aggregation model for tracking task statistics."""
    __tablename__ = "daily_analytics"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    date: datetime = Field(nullable=False, index=True)
    tasks_created: int = Field(default=0, nullable=False)
    tasks_completed: int = Field(default=0, nullable=False)
    tasks_deleted: int = Field(default=0, nullable=False)
    completion_rate: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class AnalyticsCache(SQLModel, table=True):
    """Analytics cache model for storing computed metrics."""
    __tablename__ = "analytics_cache"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    metric_name: str = Field(max_length=100, nullable=False, index=True)
    metric_value: dict = Field(sa_column=Column(JSON, nullable=False))
    expires_at: datetime = Field(nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class TaskTag(SQLModel, table=True):
    """Task tag model for organizing tasks with tags."""
    __tablename__ = "task_tags"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="tasks.id", nullable=False, index=True)
    tag: str = Field(max_length=50, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to task
    task: Optional["Task"] = Relationship(back_populates="tags")


class TaskHistory(SQLModel, table=True):
    """Task history model for tracking changes to tasks."""
    __tablename__ = "task_history"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="tasks.id", nullable=False, index=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    change_type: str = Field(max_length=50, nullable=False)
    old_value: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    new_value: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)


class TagRead(BaseModel):
    """Model for reading tag data."""
    id: UUID
    task_id: UUID
    tag: str
    created_at: datetime


class TaskHistoryRead(BaseModel):
    """Model for reading task history data."""
    id: UUID
    task_id: UUID
    user_id: UUID
    change_type: str
    old_value: Optional[dict]
    new_value: Optional[dict]
    created_at: datetime


class BatchOperationRequest(BaseModel):
    """Model for batch operation requests."""
    task_ids: List[UUID]
    operation: str
    data: Optional[dict] = None


class BatchOperationResponse(BaseModel):
    """Model for batch operation responses."""
    updated: int
    failed: int
    errors: Optional[List[dict]] = None


class UserPreferences(SQLModel, table=True):
    """User preferences model for storing user settings."""
    __tablename__ = "user_preferences"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, unique=True, index=True)
    theme: str = Field(default="system", nullable=False, regex="^(light|dark|system)$")
    language: str = Field(default="en", nullable=False, max_length=10)
    notifications: dict = Field(default_factory=dict, sa_column=Column(JSON))
    privacy: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class NotificationSettings(BaseModel):
    """Model for notification settings."""
    email_notifications: bool = True
    push_notifications: bool = False
    task_reminders: bool = True
    task_assignments: bool = True
    task_completions: bool = False
    weekly_summary: bool = True


class PrivacySettings(BaseModel):
    """Model for privacy settings."""
    profile_visibility: str = "private"  # private, contacts, public
    show_email: bool = False
    show_activity: bool = False
    show_tasks: bool = False


class PreferencesRead(BaseModel):
    """Model for reading user preferences."""
    id: UUID
    user_id: UUID
    theme: str
    language: str
    notifications: dict
    privacy: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PreferencesUpdate(BaseModel):
    """Model for updating user preferences."""
    theme: Optional[str] = Field(default=None, regex="^(light|dark|system)$")
    language: Optional[str] = Field(default=None, max_length=10)
    notifications: Optional[NotificationSettings] = None
    privacy: Optional[PrivacySettings] = None