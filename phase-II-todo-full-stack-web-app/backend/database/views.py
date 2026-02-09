"""
Database views for simplified data access and reporting.

This module creates and manages database views that provide
optimized access to commonly queried data patterns.
"""

from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseViews:
    """Manager for database views."""

    @staticmethod
    async def create_all_views(session: AsyncSession) -> Dict[str, Any]:
        """
        Create all database views.

        Args:
            session: Database session

        Returns:
            Dictionary with creation results
        """
        results = {
            "status": "success",
            "views_created": [],
            "errors": []
        }

        views = [
            DatabaseViews._create_user_task_summary_view,
            DatabaseViews._create_task_priority_view,
            DatabaseViews._create_overdue_tasks_view,
            DatabaseViews._create_completed_tasks_view,
            DatabaseViews._create_user_productivity_view,
            DatabaseViews._create_task_tags_view,
        ]

        for view_func in views:
            try:
                view_name = await view_func(session)
                results["views_created"].append(view_name)
            except Exception as e:
                results["errors"].append({
                    "view": view_func.__name__,
                    "error": str(e)
                })

        if results["errors"]:
            results["status"] = "partial_success"

        await session.commit()
        return results

    @staticmethod
    async def _create_user_task_summary_view(session: AsyncSession) -> str:
        """Create view for user task summary statistics."""
        await session.execute(text("""
            CREATE OR REPLACE VIEW user_task_summary AS
            SELECT
                u.id as user_id,
                u.email,
                u.first_name,
                u.last_name,
                COUNT(t.id) as total_tasks,
                COUNT(CASE WHEN t.completed = true THEN 1 END) as completed_tasks,
                COUNT(CASE WHEN t.completed = false THEN 1 END) as pending_tasks,
                COUNT(CASE WHEN t.completed = false AND t.due_date < NOW() THEN 1 END) as overdue_tasks,
                COUNT(CASE WHEN t.priority = 'urgent' AND t.completed = false THEN 1 END) as urgent_tasks,
                COUNT(CASE WHEN t.priority = 'high' AND t.completed = false THEN 1 END) as high_priority_tasks,
                MAX(t.created_at) as last_task_created,
                MAX(t.completed_at) as last_task_completed
            FROM users u
            LEFT JOIN tasks t ON u.id = t.user_id AND t.deleted = false
            GROUP BY u.id, u.email, u.first_name, u.last_name
        """))
        return "user_task_summary"

    @staticmethod
    async def _create_task_priority_view(session: AsyncSession) -> str:
        """Create view for tasks grouped by priority."""
        await session.execute(text("""
            CREATE OR REPLACE VIEW tasks_by_priority AS
            SELECT
                t.id,
                t.user_id,
                t.title,
                t.description,
                t.priority,
                t.status,
                t.due_date,
                t.completed,
                t.created_at,
                t.updated_at,
                u.email as user_email,
                u.first_name as user_first_name,
                u.last_name as user_last_name,
                CASE
                    WHEN t.priority = 'urgent' THEN 1
                    WHEN t.priority = 'high' THEN 2
                    WHEN t.priority = 'medium' THEN 3
                    WHEN t.priority = 'low' THEN 4
                    ELSE 5
                END as priority_order
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            WHERE t.deleted = false AND t.completed = false
            ORDER BY priority_order, t.due_date NULLS LAST, t.created_at DESC
        """))
        return "tasks_by_priority"

    @staticmethod
    async def _create_overdue_tasks_view(session: AsyncSession) -> str:
        """Create view for overdue tasks."""
        await session.execute(text("""
            CREATE OR REPLACE VIEW overdue_tasks AS
            SELECT
                t.id,
                t.user_id,
                t.title,
                t.description,
                t.priority,
                t.status,
                t.due_date,
                t.created_at,
                u.email as user_email,
                u.first_name as user_first_name,
                u.last_name as user_last_name,
                EXTRACT(DAY FROM NOW() - t.due_date) as days_overdue
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            WHERE t.deleted = false
                AND t.completed = false
                AND t.due_date < NOW()
            ORDER BY t.due_date ASC
        """))
        return "overdue_tasks"

    @staticmethod
    async def _create_completed_tasks_view(session: AsyncSession) -> str:
        """Create view for recently completed tasks."""
        await session.execute(text("""
            CREATE OR REPLACE VIEW recently_completed_tasks AS
            SELECT
                t.id,
                t.user_id,
                t.title,
                t.description,
                t.priority,
                t.status,
                t.completed_at,
                t.created_at,
                u.email as user_email,
                u.first_name as user_first_name,
                u.last_name as user_last_name,
                EXTRACT(DAY FROM t.completed_at - t.created_at) as days_to_complete
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            WHERE t.deleted = false
                AND t.completed = true
                AND t.completed_at > NOW() - INTERVAL '30 days'
            ORDER BY t.completed_at DESC
        """))
        return "recently_completed_tasks"

    @staticmethod
    async def _create_user_productivity_view(session: AsyncSession) -> str:
        """Create view for user productivity metrics."""
        await session.execute(text("""
            CREATE OR REPLACE VIEW user_productivity_metrics AS
            SELECT
                u.id as user_id,
                u.email,
                u.first_name,
                u.last_name,
                COUNT(DISTINCT DATE(t.created_at)) as active_days,
                COUNT(t.id) FILTER (WHERE t.completed = true) as total_completed,
                COUNT(t.id) FILTER (WHERE t.completed = true AND t.completed_at > NOW() - INTERVAL '7 days') as completed_last_7_days,
                COUNT(t.id) FILTER (WHERE t.completed = true AND t.completed_at > NOW() - INTERVAL '30 days') as completed_last_30_days,
                AVG(EXTRACT(EPOCH FROM (t.completed_at - t.created_at)) / 86400) FILTER (WHERE t.completed = true) as avg_days_to_complete,
                COUNT(t.id) FILTER (WHERE t.completed = true AND t.completed_at < t.due_date) as completed_before_due,
                COUNT(t.id) FILTER (WHERE t.completed = true AND t.completed_at > t.due_date) as completed_after_due
            FROM users u
            LEFT JOIN tasks t ON u.id = t.user_id AND t.deleted = false
            GROUP BY u.id, u.email, u.first_name, u.last_name
        """))
        return "user_productivity_metrics"

    @staticmethod
    async def _create_task_tags_view(session: AsyncSession) -> str:
        """Create view for tasks with their tags."""
        await session.execute(text("""
            CREATE OR REPLACE VIEW tasks_with_tags AS
            SELECT
                t.id as task_id,
                t.user_id,
                t.title,
                t.description,
                t.priority,
                t.status,
                t.completed,
                t.due_date,
                t.created_at,
                array_agg(tt.tag) FILTER (WHERE tt.tag IS NOT NULL) as tags,
                COUNT(tt.id) as tag_count
            FROM tasks t
            LEFT JOIN task_tags tt ON t.id = tt.task_id
            WHERE t.deleted = false
            GROUP BY t.id, t.user_id, t.title, t.description, t.priority, t.status, t.completed, t.due_date, t.created_at
        """))
        return "tasks_with_tags"

    @staticmethod
    async def drop_all_views(session: AsyncSession) -> Dict[str, Any]:
        """
        Drop all database views.

        Args:
            session: Database session

        Returns:
            Dictionary with drop results
        """
        views = [
            "user_task_summary",
            "tasks_by_priority",
            "overdue_tasks",
            "recently_completed_tasks",
            "user_productivity_metrics",
            "tasks_with_tags",
            "recent_user_activity",
            "task_change_summary"
        ]

        results = {
            "status": "success",
            "views_dropped": [],
            "errors": []
        }

        for view_name in views:
            try:
                await session.execute(text(f"DROP VIEW IF EXISTS {view_name} CASCADE"))
                results["views_dropped"].append(view_name)
            except Exception as e:
                results["errors"].append({
                    "view": view_name,
                    "error": str(e)
                })

        await session.commit()
        return results

    @staticmethod
    async def refresh_materialized_views(session: AsyncSession) -> Dict[str, Any]:
        """
        Refresh materialized views if any exist.

        Note: Currently we use regular views. This method is a placeholder
        for future materialized views that need periodic refresh.

        Args:
            session: Database session

        Returns:
            Dictionary with refresh results
        """
        return {
            "status": "info",
            "message": "No materialized views to refresh. All views are regular views that update automatically."
        }


async def initialize_views(session: AsyncSession) -> Dict[str, Any]:
    """
    Initialize all database views.

    Args:
        session: Database session

    Returns:
        Dictionary with initialization results
    """
    print("Initializing database views...")
    result = await DatabaseViews.create_all_views(session)

    if result["status"] == "success":
        print(f"✓ Successfully created {len(result['views_created'])} views")
        for view in result["views_created"]:
            print(f"  - {view}")
    elif result["status"] == "partial_success":
        print(f"⚠ Created {len(result['views_created'])} views with {len(result['errors'])} errors")
        for error in result["errors"]:
            print(f"  ✗ {error['view']}: {error['error']}")
    else:
        print("✗ Failed to create views")

    return result
