"""Task schemas for request/response models"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = None
    description: Optional[str] = None


class TaskResponse(BaseModel):
    """Schema for task response"""
    id: str
    title: str
    description: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
