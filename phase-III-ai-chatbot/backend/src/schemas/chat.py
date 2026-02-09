"""Chat schemas for request/response models"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class ChatRequest(BaseModel):
    """Schema for chat request"""
    conversation_id: Optional[UUID] = None
    message: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    """Schema for chat response"""
    conversation_id: str
    response: str
    created_at: str
