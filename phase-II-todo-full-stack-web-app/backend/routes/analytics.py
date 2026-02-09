"""
Analytics API routes for task statistics and reporting.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from middleware.auth import get_current_user
from models import User
from schemas.analytics import (
    OverviewStats,
    TrendData,
    CompletionRateResponse,
    PriorityDistributionResponse,
    PriorityDistribution,
    DueDateAdherenceResponse,
    ProductivityScoreResponse,
    AnalyticsErrorResponse
)
from services import analytics as analytics_service
from services.cache import get_or_compute_metric
from services import export as export_service
from services import recommendations as recommendations_service
from fastapi.responses import Response


router = APIRouter(
    prefix="/api/v1/users/{user_id}/analytics",
    tags=["analytics"],
    responses={
        401: {"model": AnalyticsErrorResponse, "description": "Unauthorized"},
        403: {"model": AnalyticsErrorResponse, "description": "Forbidden"},
        404: {"model": AnalyticsErrorResponse, "description": "Not Found"}
    }
)


def verify_user_access(user_id: UUID, current_user: User) -> None:
    """
    Verify that the authenticated user matches the requested user_id.

    Args:
        user_id: Requested user ID from URL
        current_user: Authenticated user

    Raises:
        HTTPException: If user IDs don't match
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own analytics"
        )


@router.get(
    "/overview",
    response_model=OverviewStats,
    summary="Get analytics overview",
    description="Retrieve comprehensive task statistics and metrics overview"
)
async def get_analytics_overview(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get analytics overview with all key metrics.

    Returns:
        - Total tasks count
        - Completed and pending tasks
        - Completion rate
        - Overdue tasks count
        - Tasks completed today, this week, this month
        - Average completion time
        - Distribution by priority
        - Distribution by status
    """
    verify_user_access(user_id, current_user)

    try:
        # Get task totals
        totals = await analytics_service.calculate_task_totals(db, user_id)

        # Get completion stats
        completion_stats = await analytics_service.get_completion_stats(db, user_id)

        # Get completion rate
        completion_rate = await analytics_service.calculate_completion_rate(db, user_id)

        # Get overdue count
        overdue_count = await analytics_service.get_overdue_count(db, user_id)

        # Get priority distribution
        priority_dist = await analytics_service.get_priority_distribution(db, user_id)

        # Get status distribution
        status_dist = await analytics_service.get_status_distribution(db, user_id)

        # Get average completion time
        avg_completion_time = await analytics_service.calculate_average_completion_time(db, user_id)

        return OverviewStats(
            total_tasks=totals["total"],
            completed_tasks=totals["completed"],
            pending_tasks=totals["pending"],
            completion_rate=completion_rate,
            overdue_tasks=overdue_count,
            tasks_completed_today=completion_stats["today"],
            tasks_completed_this_week=completion_stats["this_week"],
            tasks_completed_this_month=completion_stats["this_month"],
            average_completion_time=avg_completion_time,
            by_priority=priority_dist,
            by_status=status_dist
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics overview: {str(e)}"
        )


@router.get(
    "/trends",
    response_model=TrendData,
    summary="Get task trends",
    description="Retrieve task trends over time with customizable period"
)
async def get_analytics_trends(
    user_id: UUID,
    period: str = Query("weekly", regex="^(daily|weekly|monthly)$", description="Period type"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get task trends over time.

    Query Parameters:
        - period: Period type (daily, weekly, monthly)
        - start_date: Optional start date in ISO format
        - end_date: Optional end date in ISO format

    Returns:
        Trend data with tasks created, completed, and completion rate over time
    """
    verify_user_access(user_id, current_user)

    try:
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        # Get trend data
        trend_data = await analytics_service.calculate_trends(
            db, user_id, period, start_dt, end_dt
        )

        return TrendData(
            period=period,
            data=trend_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trends: {str(e)}"
        )


@router.get(
    "/completion-rate",
    response_model=CompletionRateResponse,
    summary="Get completion rate",
    description="Retrieve completion rate for a specified period"
)
async def get_completion_rate(
    user_id: UUID,
    period: str = Query("30days", regex="^(7days|30days|90days|year)$", description="Analysis period"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get completion rate for a specified period.

    Query Parameters:
        - period: Analysis period (7days, 30days, 90days, year)

    Returns:
        Completion rate, total tasks, completed tasks, and trend direction
    """
    verify_user_access(user_id, current_user)

    try:
        # Get current period completion rate
        completion_rate = await analytics_service.calculate_completion_rate(db, user_id)
        totals = await analytics_service.calculate_task_totals(db, user_id)

        # For simplicity, trend is "stable" - can be enhanced with historical comparison
        trend = "stable"

        return CompletionRateResponse(
            period=period,
            completion_rate=completion_rate,
            total_tasks=totals["total"],
            completed_tasks=totals["completed"],
            trend=trend,
            previous_period_rate=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve completion rate: {str(e)}"
        )


@router.get(
    "/priority-distribution",
    response_model=PriorityDistributionResponse,
    summary="Get priority distribution",
    description="Retrieve task distribution by priority level"
)
async def get_priority_distribution(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get task distribution by priority level.

    Returns:
        Distribution of tasks across priority levels with counts and percentages
    """
    verify_user_access(user_id, current_user)

    try:
        # Get priority distribution
        priority_dist = await analytics_service.get_priority_distribution(db, user_id)
        totals = await analytics_service.calculate_task_totals(db, user_id)

        total_tasks = totals["total"]

        # Calculate percentages
        distribution = []
        for priority, count in priority_dist.items():
            percentage = (count / total_tasks * 100) if total_tasks > 0 else 0.0
            distribution.append(
                PriorityDistribution(
                    priority=priority,
                    count=count,
                    percentage=round(percentage, 2)
                )
            )

        return PriorityDistributionResponse(
            distribution=distribution,
            total_tasks=total_tasks
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve priority distribution: {str(e)}"
        )


@router.get(
    "/due-date-adherence",
    response_model=DueDateAdherenceResponse,
    summary="Get due date adherence",
    description="Retrieve due date adherence metrics"
)
async def get_due_date_adherence(
    user_id: UUID,
    period: str = Query("30days", regex="^(30days|90days|year)$", description="Analysis period"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get due date adherence metrics.

    Query Parameters:
        - period: Analysis period (30days, 90days, year)

    Returns:
        On-time tasks, late tasks, adherence rate, and average delay
    """
    verify_user_access(user_id, current_user)

    try:
        # Parse period to days
        period_map = {
            "30days": 30,
            "90days": 90,
            "year": 365
        }
        period_days = period_map.get(period, 30)

        # Get adherence data
        adherence_data = await analytics_service.calculate_adherence_rate(db, user_id, period_days)

        # Get count of tasks without due dates
        totals = await analytics_service.calculate_task_totals(db, user_id)
        tasks_with_due_date = adherence_data["on_time"] + adherence_data["late"]
        no_due_date = totals["total"] - tasks_with_due_date

        return DueDateAdherenceResponse(
            period=period,
            on_time=adherence_data["on_time"],
            late=adherence_data["late"],
            no_due_date=no_due_date,
            adherence_rate=adherence_data["adherence_rate"],
            average_delay=adherence_data["average_delay"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve due date adherence: {str(e)}"
        )


@router.get(
    "/productivity-score",
    response_model=ProductivityScoreResponse,
    summary="Get productivity score",
    description="Retrieve overall productivity score with contributing factors"
)
async def get_productivity_score(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall productivity score.

    Returns:
        Productivity score (0-100), contributing factors, trend, and recommendations
    """
    verify_user_access(user_id, current_user)

    try:
        # Calculate productivity score
        score_data = await analytics_service.calculate_productivity_score(db, user_id)

        # Generate simple recommendations based on scores
        recommendations = []
        if score_data["factors"]["completion_rate"] < 50:
            recommendations.append("Focus on completing existing tasks before creating new ones")
        if score_data["factors"]["due_date_adherence"] < 70:
            recommendations.append("Set more realistic due dates to improve adherence")
        if score_data["factors"]["task_velocity"] < 50:
            recommendations.append("Break down large tasks into smaller, manageable pieces")

        if not recommendations:
            recommendations.append("Great work! Keep maintaining your productivity habits")

        # Determine trend (simplified - can be enhanced with historical data)
        trend = "stable"
        if score_data["score"] >= 80:
            trend = "improving"
        elif score_data["score"] < 50:
            trend = "declining"

        return ProductivityScoreResponse(
            score=score_data["score"],
            factors=score_data["factors"],
            trend=trend,
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve productivity score: {str(e)}"
        )


@router.get(
    "/export",
    summary="Export analytics data",
    description="Export task and analytics data in CSV or JSON format"
)
async def export_analytics_data(
    user_id: UUID,
    format: str = Query("csv", regex="^(csv|json)$", description="Export format"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Export analytics data in CSV or JSON format.

    Query Parameters:
        - format: Export format (csv or json)
        - start_date: Optional start date filter (ISO format)
        - end_date: Optional end date filter (ISO format)

    Returns:
        File content in requested format
    """
    verify_user_access(user_id, current_user)

    try:
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        # Export data based on format
        if format == "csv":
            content = await export_service.export_to_csv(db, user_id, start_dt, end_dt)
            media_type = "text/csv"
            filename = f"tasks_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        else:  # json
            content = await export_service.export_to_json(db, user_id, start_dt, end_dt)
            media_type = "application/json"
            filename = f"tasks_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


@router.get(
    "/recommendations",
    summary="Get productivity recommendations",
    description="Get personalized productivity recommendations based on task patterns"
)
async def get_recommendations(
    user_id: UUID,
    limit: int = Query(5, ge=1, le=10, description="Maximum number of recommendations"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized productivity recommendations.

    Query Parameters:
        - limit: Maximum number of recommendations to return (1-10)

    Returns:
        List of recommendations with type, priority, message, and action
    """
    verify_user_access(user_id, current_user)

    try:
        # Generate recommendations
        recommendations = await recommendations_service.generate_recommendations(db, user_id)

        # Limit results
        limited_recommendations = recommendations[:limit]

        return {
            "total_recommendations": len(recommendations),
            "returned_count": len(limited_recommendations),
            "recommendations": limited_recommendations
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
