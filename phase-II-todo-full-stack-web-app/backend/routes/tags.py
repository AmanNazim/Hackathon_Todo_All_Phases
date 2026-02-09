"""
Tag management routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from database import get_session
from auth import get_current_user
from models import User, Task, TaskTag
from services.task_organization import get_tag_statistics, get_all_user_tags

router = APIRouter()


@router.get("/api/v1/users/{user_id}/tags/statistics")
async def get_tag_stats(
    user_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get tag usage statistics for a user.

    Returns:
        Dictionary with tag names and usage counts
    """
    # Verify user access
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    stats = get_tag_statistics(session, user_id)

    return {
        "tags": stats,
        "total_tags": len(stats),
        "total_usage": sum(stats.values())
    }


@router.get("/api/v1/users/{user_id}/tags/autocomplete")
async def autocomplete_tags(
    user_id: str,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get tag suggestions for autocomplete.

    Args:
        q: Search query
        limit: Maximum number of suggestions

    Returns:
        List of matching tag names
    """
    # Verify user access
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get all user tags and filter by query
    all_tags = get_all_user_tags(session, user_id)

    # Case-insensitive matching
    query_lower = q.lower()
    matching_tags = [
        tag for tag in all_tags
        if query_lower in tag.lower()
    ]

    # Sort by relevance (starts with query first, then contains)
    starts_with = [tag for tag in matching_tags if tag.lower().startswith(query_lower)]
    contains = [tag for tag in matching_tags if not tag.lower().startswith(query_lower)]

    results = (starts_with + contains)[:limit]

    return {
        "suggestions": results,
        "count": len(results)
    }
