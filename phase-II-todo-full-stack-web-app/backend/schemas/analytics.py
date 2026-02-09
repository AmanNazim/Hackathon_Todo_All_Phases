"""
Pydantic schemas for analytics API responses.
"""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class PriorityDistribution(BaseModel):
    """Schema for priority distribution data."""
    priority: str = Field(..., description="Priority level (low, medium, high, urgent)")
    count: int = Field(..., description="Number of tasks with this priority")
    percentage: float = Field(..., description="Percentage of total tasks")


class StatusDistribution(BaseModel):
    """Schema for status distribution data."""
    status: str = Field(..., description="Task status")
    count: int = Field(..., description="Number of tasks with this status")
    percentage: float = Field(..., description="Percentage of total tasks")


class OverviewStats(BaseModel):
    """Schema for overview statistics response."""
    total_tasks: int = Field(..., description="Total number of tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    pending_tasks: int = Field(..., description="Number of pending tasks")
    completion_rate: float = Field(..., description="Completion rate percentage")
    overdue_tasks: int = Field(..., description="Number of overdue tasks")
    tasks_completed_today: int = Field(..., description="Tasks completed today")
    tasks_completed_this_week: int = Field(..., description="Tasks completed this week")
    tasks_completed_this_month: int = Field(..., description="Tasks completed this month")
    average_completion_time: Optional[str] = Field(None, description="Average time to complete tasks")
    by_priority: Dict[str, int] = Field(..., description="Task count by priority")
    by_status: Dict[str, int] = Field(..., description="Task count by status")


class TrendDataPoint(BaseModel):
    """Schema for a single trend data point."""
    date: str = Field(..., description="Date in ISO format")
    tasks_created: int = Field(..., description="Tasks created on this date")
    tasks_completed: int = Field(..., description="Tasks completed on this date")
    completion_rate: float = Field(..., description="Completion rate for this period")


class TrendData(BaseModel):
    """Schema for trend data response."""
    period: str = Field(..., description="Period type (daily, weekly, monthly)")
    data: List[TrendDataPoint] = Field(..., description="List of trend data points")


class CompletionRateResponse(BaseModel):
    """Schema for completion rate response."""
    period: str = Field(..., description="Period analyzed (7days, 30days, 90days, year)")
    completion_rate: float = Field(..., description="Completion rate percentage")
    total_tasks: int = Field(..., description="Total tasks in period")
    completed_tasks: int = Field(..., description="Completed tasks in period")
    trend: str = Field(..., description="Trend direction (increasing, decreasing, stable)")
    previous_period_rate: Optional[float] = Field(None, description="Previous period completion rate")


class PriorityDistributionResponse(BaseModel):
    """Schema for priority distribution response."""
    distribution: List[PriorityDistribution] = Field(..., description="Priority distribution data")
    total_tasks: int = Field(..., description="Total number of tasks")


class DueDateAdherenceResponse(BaseModel):
    """Schema for due date adherence response."""
    period: str = Field(..., description="Period analyzed")
    on_time: int = Field(..., description="Tasks completed on time")
    late: int = Field(..., description="Tasks completed late")
    no_due_date: int = Field(..., description="Tasks without due date")
    adherence_rate: float = Field(..., description="Adherence rate percentage")
    average_delay: Optional[str] = Field(None, description="Average delay for late tasks")


class ProductivityFactors(BaseModel):
    """Schema for productivity score factors."""
    completion_rate: float = Field(..., description="Completion rate score (0-100)")
    due_date_adherence: float = Field(..., description="Due date adherence score (0-100)")
    task_velocity: float = Field(..., description="Task velocity score (0-100)")


class ProductivityScoreResponse(BaseModel):
    """Schema for productivity score response."""
    score: float = Field(..., description="Overall productivity score (0-100)")
    factors: ProductivityFactors = Field(..., description="Individual factor scores")
    trend: str = Field(..., description="Trend direction (improving, declining, stable)")
    recommendations: List[str] = Field(..., description="Productivity improvement recommendations")


class AnalyticsErrorResponse(BaseModel):
    """Schema for analytics error responses."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
