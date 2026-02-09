"""
Database migration to create materialized views for analytics.

This migration creates materialized views for common analytics aggregations
to improve query performance.

Revision ID: 006_create_analytics_views
Revises: 005_analytics_indexes
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_create_analytics_views'
down_revision = '005_analytics_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create materialized views for analytics.
    """
    # Create materialized view for user task statistics
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS user_task_stats AS
        SELECT
            user_id,
            COUNT(*) as total_tasks,
            COUNT(*) FILTER (WHERE status = 'done') as completed_tasks,
            COUNT(*) FILTER (WHERE status != 'done' AND NOT deleted) as pending_tasks,
            COUNT(*) FILTER (WHERE deleted) as deleted_tasks,
            COUNT(*) FILTER (WHERE due_date < NOW() AND status != 'done' AND NOT deleted) as overdue_tasks,
            ROUND(
                (COUNT(*) FILTER (WHERE status = 'done')::numeric /
                NULLIF(COUNT(*) FILTER (WHERE NOT deleted), 0) * 100), 2
            ) as completion_rate
        FROM tasks
        GROUP BY user_id;
    """)

    # Create index on materialized view
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_user_task_stats_user_id
        ON user_task_stats(user_id);
    """)

    # Create materialized view for priority distribution
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS user_priority_distribution AS
        SELECT
            user_id,
            priority,
            COUNT(*) as task_count
        FROM tasks
        WHERE NOT deleted
        GROUP BY user_id, priority;
    """)

    # Create index on materialized view
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_priority_dist_user_id
        ON user_priority_distribution(user_id);
    """)

    # Create materialized view for status distribution
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS user_status_distribution AS
        SELECT
            user_id,
            status,
            COUNT(*) as task_count
        FROM tasks
        WHERE NOT deleted
        GROUP BY user_id, status;
    """)

    # Create index on materialized view
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_status_dist_user_id
        ON user_status_distribution(user_id);
    """)

    # Create materialized view for monthly trends
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS user_monthly_trends AS
        SELECT
            user_id,
            DATE_TRUNC('month', created_at) as month,
            COUNT(*) as tasks_created,
            COUNT(*) FILTER (WHERE status = 'done') as tasks_completed,
            COUNT(*) FILTER (WHERE deleted) as tasks_deleted
        FROM tasks
        GROUP BY user_id, DATE_TRUNC('month', created_at);
    """)

    # Create index on materialized view
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_monthly_trends_user_month
        ON user_monthly_trends(user_id, month);
    """)

    print("✓ Created materialized views for analytics")


def downgrade() -> None:
    """
    Drop materialized views.
    """
    op.execute("DROP MATERIALIZED VIEW IF EXISTS user_monthly_trends CASCADE;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS user_status_distribution CASCADE;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS user_priority_distribution CASCADE;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS user_task_stats CASCADE;")

    print("✓ Dropped materialized views")
