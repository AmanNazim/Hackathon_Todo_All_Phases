"""
Audit trail and change tracking system for the Todo application.

This module provides comprehensive audit logging for all data changes,
enabling compliance, debugging, and historical analysis.
"""

from datetime import datetime, UTC
from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from models import TaskHistory


class AuditLogger:
    """Audit logging system for tracking data changes."""

    @staticmethod
    async def log_task_change(
        session: AsyncSession,
        task_id: UUID,
        user_id: UUID,
        change_type: str,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None
    ) -> TaskHistory:
        """
        Log a change to a task.

        Args:
            session: Database session
            task_id: ID of the task that changed
            user_id: ID of the user who made the change
            change_type: Type of change (created, updated, deleted, completed, etc.)
            old_value: Previous values (for updates)
            new_value: New values (for updates and creates)

        Returns:
            TaskHistory record
        """
        history_entry = TaskHistory(
            task_id=task_id,
            user_id=user_id,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value,
            created_at=datetime.now(UTC)
        )

        session.add(history_entry)
        await session.commit()
        await session.refresh(history_entry)

        return history_entry

    @staticmethod
    async def get_task_history(
        session: AsyncSession,
        task_id: UUID,
        limit: int = 50
    ) -> List[TaskHistory]:
        """
        Get the change history for a specific task.

        Args:
            session: Database session
            task_id: ID of the task
            limit: Maximum number of history entries to return

        Returns:
            List of TaskHistory records
        """
        from sqlmodel import select

        statement = (
            select(TaskHistory)
            .where(TaskHistory.task_id == task_id)
            .order_by(TaskHistory.created_at.desc())
            .limit(limit)
        )

        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def get_user_activity(
        session: AsyncSession,
        user_id: UUID,
        limit: int = 100
    ) -> List[TaskHistory]:
        """
        Get recent activity for a specific user.

        Args:
            session: Database session
            user_id: ID of the user
            limit: Maximum number of activity entries to return

        Returns:
            List of TaskHistory records
        """
        from sqlmodel import select

        statement = (
            select(TaskHistory)
            .where(TaskHistory.user_id == user_id)
            .order_by(TaskHistory.created_at.desc())
            .limit(limit)
        )

        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def get_audit_statistics(
        session: AsyncSession,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get audit trail statistics.

        Args:
            session: Database session
            user_id: Optional user ID to filter by

        Returns:
            Dictionary with audit statistics
        """
        try:
            # Build query based on whether user_id is provided
            if user_id:
                query = text("""
                    SELECT
                        change_type,
                        COUNT(*) as count,
                        MAX(created_at) as last_occurrence
                    FROM task_history
                    WHERE user_id = :user_id
                    GROUP BY change_type
                    ORDER BY count DESC
                """)
                result = await session.execute(query, {"user_id": str(user_id)})
            else:
                query = text("""
                    SELECT
                        change_type,
                        COUNT(*) as count,
                        MAX(created_at) as last_occurrence
                    FROM task_history
                    GROUP BY change_type
                    ORDER BY count DESC
                """)
                result = await session.execute(query)

            changes_by_type = {}
            total_changes = 0

            for row in result:
                change_type = row[0]
                count = row[1]
                last_occurrence = row[2]

                changes_by_type[change_type] = {
                    "count": count,
                    "last_occurrence": last_occurrence.isoformat() if last_occurrence else None
                }
                total_changes += count

            return {
                "status": "success",
                "total_changes": total_changes,
                "changes_by_type": changes_by_type,
                "user_id": str(user_id) if user_id else "all_users"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get audit statistics: {str(e)}"
            }

    @staticmethod
    async def cleanup_old_audit_logs(
        session: AsyncSession,
        days_to_keep: int = 90
    ) -> Dict[str, Any]:
        """
        Clean up audit logs older than specified days.

        Args:
            session: Database session
            days_to_keep: Number of days of audit logs to retain

        Returns:
            Dictionary with cleanup results
        """
        try:
            query = text("""
                DELETE FROM task_history
                WHERE created_at < NOW() - INTERVAL ':days days'
                RETURNING id
            """)

            result = await session.execute(query, {"days": days_to_keep})
            deleted_count = len(result.fetchall())
            await session.commit()

            return {
                "status": "success",
                "deleted_count": deleted_count,
                "days_kept": days_to_keep,
                "message": f"Deleted {deleted_count} audit log entries older than {days_to_keep} days"
            }
        except Exception as e:
            await session.rollback()
            return {
                "status": "error",
                "message": f"Cleanup failed: {str(e)}"
            }


class ChangeTracker:
    """Track changes to model instances for audit logging."""

    @staticmethod
    def get_changed_fields(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Compare two dictionaries and return changed fields.

        Args:
            old_data: Original data
            new_data: Updated data

        Returns:
            Dictionary of changed fields with old and new values
        """
        changes = {}

        # Check for changed or new fields
        for key, new_value in new_data.items():
            old_value = old_data.get(key)
            if old_value != new_value:
                changes[key] = {
                    "old": old_value,
                    "new": new_value
                }

        return changes

    @staticmethod
    def format_change_summary(changes: Dict[str, Dict[str, Any]]) -> str:
        """
        Format changes into a human-readable summary.

        Args:
            changes: Dictionary of changed fields

        Returns:
            Formatted string summary
        """
        if not changes:
            return "No changes"

        summary_parts = []
        for field, values in changes.items():
            old = values.get("old", "None")
            new = values.get("new", "None")
            summary_parts.append(f"{field}: {old} → {new}")

        return "; ".join(summary_parts)


# Audit event types
class AuditEventType:
    """Standard audit event types."""
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_COMPLETED = "task_completed"
    TASK_UNCOMPLETED = "task_uncompleted"
    TASK_PRIORITY_CHANGED = "task_priority_changed"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_DUE_DATE_CHANGED = "task_due_date_changed"
    TAG_ADDED = "tag_added"
    TAG_REMOVED = "tag_removed"


async def create_audit_views(session: AsyncSession) -> Dict[str, Any]:
    """
    Create database views for audit trail analysis.

    Args:
        session: Database session

    Returns:
        Dictionary with creation results
    """
    try:
        # View for recent changes by user
        await session.execute(text("""
            CREATE OR REPLACE VIEW recent_user_activity AS
            SELECT
                th.user_id,
                u.email,
                u.first_name,
                u.last_name,
                th.change_type,
                COUNT(*) as change_count,
                MAX(th.created_at) as last_change
            FROM task_history th
            JOIN users u ON th.user_id = u.id
            WHERE th.created_at > NOW() - INTERVAL '30 days'
            GROUP BY th.user_id, u.email, u.first_name, u.last_name, th.change_type
            ORDER BY last_change DESC
        """))

        # View for task change summary
        await session.execute(text("""
            CREATE OR REPLACE VIEW task_change_summary AS
            SELECT
                t.id as task_id,
                t.title,
                t.user_id,
                COUNT(th.id) as total_changes,
                MIN(th.created_at) as first_change,
                MAX(th.created_at) as last_change,
                array_agg(DISTINCT th.change_type) as change_types
            FROM tasks t
            LEFT JOIN task_history th ON t.id = th.task_id
            GROUP BY t.id, t.title, t.user_id
            ORDER BY total_changes DESC
        """))

        await session.commit()

        return {
            "status": "success",
            "message": "Audit views created successfully",
            "views": [
                "recent_user_activity",
                "task_change_summary"
            ]
        }
    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "message": f"Failed to create audit views: {str(e)}"
        }
