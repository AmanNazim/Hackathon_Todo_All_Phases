"""Add analytics performance indexes

Revision ID: 005_analytics_indexes
Revises: 004_create_analytics_cache
Create Date: 2026-02-09 06:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_analytics_indexes'
down_revision = '004_create_analytics_cache'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add composite indexes on tasks table for analytics queries
    op.create_index(
        'idx_tasks_user_completed',
        'tasks',
        ['user_id', 'completed']
    )

    op.create_index(
        'idx_tasks_user_priority',
        'tasks',
        ['user_id', 'priority']
    )

    op.create_index(
        'idx_tasks_user_due_date',
        'tasks',
        ['user_id', 'due_date']
    )

    op.create_index(
        'idx_tasks_completed_updated_at',
        'tasks',
        ['completed', 'updated_at']
    )

    op.create_index(
        'idx_tasks_user_completed_updated',
        'tasks',
        ['user_id', 'completed', 'updated_at']
    )

    # Add index for overdue tasks query
    op.create_index(
        'idx_tasks_user_completed_due_date',
        'tasks',
        ['user_id', 'completed', 'due_date']
    )


def downgrade() -> None:
    # Drop indexes in reverse order
    op.drop_index('idx_tasks_user_completed_due_date', table_name='tasks')
    op.drop_index('idx_tasks_user_completed_updated', table_name='tasks')
    op.drop_index('idx_tasks_completed_updated_at', table_name='tasks')
    op.drop_index('idx_tasks_user_due_date', table_name='tasks')
    op.drop_index('idx_tasks_user_priority', table_name='tasks')
    op.drop_index('idx_tasks_user_completed', table_name='tasks')
