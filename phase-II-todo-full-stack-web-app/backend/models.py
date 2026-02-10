"""
Database models for the Todo application using SQLModel.

Note: This file includes Better Auth tables created by SQLModel.
Better Auth will use these tables for authentication.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import JSON, Text, ForeignKey
from pydantic import BaseModel, EmailStr


# ============================================================================
# Better Auth Tables (Created by SQLModel)
# ============================================================================

class BetterAuthUser(SQLModel, table=True):
    """Better Auth user table - created by SQLModel."""
    __tablename__ = "user"

    id: str = Field(sa_column=Column(Text, primary_key=True))
    email: str = Field(sa_column=Column(Text, nullable=False, unique=True))
    emailVerified: bool = Field(default=False)
    name: Optional[str] = Field(default=None, sa_column=Column(Text))
    image: Optional[str] = Field(default=None, sa_column=Column(Text))
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


# Alias for backward compatibility with existing code
User = BetterAuthUser


class BetterAuthSession(SQLModel, table=True):
    """Better Auth session table - created by SQLModel."""
    __tablename__ = "session"

    id: str = Field(sa_column=Column(Text, primary_key=True))
    userId: str = Field(sa_column=Column(Text, ForeignKey("user.id"), nullable=False, index=True))
    expiresAt: datetime
    token: str = Field(sa_column=Column(Text, nullable=False, unique=True))
    ipAddress: Optional[str] = Field(default=None, sa_column=Column(Text))
    userAgent: Optional[str] = Field(default=None, sa_column=Column(Text))
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


class BetterAuthAccount(SQLModel, table=True):
    """Better Auth account table - created by SQLModel."""
    __tablename__ = "account"

    id: str = Field(sa_column=Column(Text, primary_key=True))
    userId: str = Field(sa_column=Column(Text, ForeignKey("user.id"), nullable=False, index=True))
    accountId: str = Field(sa_column=Column(Text, nullable=False))
    providerId: str = Field(sa_column=Column(Text, nullable=False))
    accessToken: Optional[str] = Field(default=None, sa_column=Column(Text))
    refreshToken: Optional[str] = Field(default=None, sa_column=Column(Text))
    idToken: Optional[str] = Field(default=None, sa_column=Column(Text))
    expiresAt: Optional[datetime] = Field(default=None)
    password: Optional[str] = Field(default=None, sa_column=Column(Text))
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


class BetterAuthVerification(SQLModel, table=True):
    """Better Auth verification table - created by SQLModel."""
    __tablename__ = "verification"

    id: str = Field(sa_column=Column(Text, primary_key=True))
    identifier: str = Field(sa_column=Column(Text, nullable=False, index=True))
    value: str = Field(sa_column=Column(Text, nullable=False))
    expiresAt: datetime
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# User Profile Models (for API responses)
# ============================================================================

class UserRead(BaseModel):
    """Model for reading user data from Better Auth."""
    id: str
    email: str
    name: Optional[str]
    emailVerified: bool
    image: Optional[str]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ProfileRead(BaseModel):
    """Model for reading user profile data."""
    id: str
    email: str
    name: Optional[str]
    emailVerified: bool
    image: Optional[str]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    """Model for updating user profile data."""
    name: Optional[str] = None
    image: Optional[str] = None


# ============================================================================
# Application Tables (Tasks, Analytics, etc.)
# ============================================================================

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
    user_id: str = Field(foreign_key="user.id", nullable=False, index=True)  # References Better Auth's user table
    deleted: bool = Field(default=False, nullable=False, index=True)
    deleted_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    # Relationship to tags
    tags: List["TaskTag"] = Relationship(back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class TaskCreate(TaskBase):
    """Model for creating new tasks."""
    pass


class TaskRead(TaskBase):
    """Model for reading task data."""
    id: UUID
    user_id: str  # Better Auth uses TEXT for user IDs
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
    user_id: str = Field(foreign_key="user.id", nullable=False, index=True)  # References Better Auth's user table
    token_hash: str = Field(nullable=False)
    expires_at: datetime = Field(nullable=False, index=True)
    used: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class EmailVerificationToken(SQLModel, table=True):
    """Email verification token model."""
    __tablename__ = "email_verification_tokens"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="user.id", nullable=False, index=True)  # References Better Auth's user table
    token_hash: str = Field(nullable=False)
    expires_at: datetime = Field(nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class DailyAnalytics(SQLModel, table=True):
    """Daily analytics aggregation model for tracking task statistics."""
    __tablename__ = "daily_analytics"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="user.id", nullable=False, index=True)  # References Better Auth's user table
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
    user_id: str = Field(foreign_key="user.id", nullable=False, index=True)  # References Better Auth's user table
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
    user_id: str = Field(foreign_key="user.id", nullable=False)  # References Better Auth's user table
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
    user_id: str  # Better Auth uses TEXT for user IDs
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
    user_id: str = Field(foreign_key="user.id", nullable=False, unique=True, index=True)  # References Better Auth's user table
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
    user_id: str  # Better Auth uses TEXT for user IDs
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