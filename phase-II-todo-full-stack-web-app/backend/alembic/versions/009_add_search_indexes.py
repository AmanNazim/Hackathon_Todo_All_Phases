"""Add full-text search indexes for task search optimization.

Revision ID: 009_add_search_indexes
Revises: 008_create_task_history
Create Date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009_add_search_indexes'
down_revision = '008_create_task_history'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add GIN indexes for full-text search on tasks."""

    # Add tsvector column for full-text search
    op.execute("""
        ALTER TABLE tasks
        ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('english', coalesce(description, '')), 'B')
        ) STORED;
    """)

    # Create GIN index on search_vector for fast full-text search
    op.create_index(
        'idx_tasks_search_vector',
        'tasks',
        ['search_vector'],
        postgresql_using='gin'
    )

    # Create additional indexes for common query patterns
    op.create_index(
        'idx_tasks_user_status_priority',
        'tasks',
        ['user_id', 'status', 'priority'],
        postgresql_where=sa.text('deleted = false')
    )

    op.create_index(
        'idx_tasks_user_due_date',
        'tasks',
        ['user_id', 'due_date'],
        postgresql_where=sa.text('deleted = false AND due_date IS NOT NULL')
    )

    op.create_index(
        'idx_tasks_user_completed_at',
        'tasks',
        ['user_id', 'completed_at'],
        postgresql_where=sa.text('deleted = false AND completed_at IS NOT NULL')
    )


def downgrade() -> None:
    """Remove search indexes."""

    # Drop indexes
    op.drop_index('idx_tasks_user_completed_at', table_name='tasks')
    op.drop_index('idx_tasks_user_due_date', table_name='tasks')
    op.drop_index('idx_tasks_user_status_priority', table_name='tasks')
    op.drop_index('idx_tasks_search_vector', table_name='tasks')

    # Drop search_vector column
    op.execute("ALTER TABLE tasks DROP COLUMN search_vector;")
