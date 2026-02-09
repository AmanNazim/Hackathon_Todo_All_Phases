"""Add status and soft delete fields to tasks table

Revision ID: 006_add_task_status_fields
Revises: 005_analytics_indexes
Create Date: 2026-02-09 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006_add_task_status_fields'
down_revision = '005_analytics_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add status field to tasks table
    op.add_column('tasks', sa.Column('status', sa.String(20), nullable=False, server_default='todo'))

    # Add completed_at field to tasks table
    op.add_column('tasks', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))

    # Add soft delete fields to tasks table
    op.add_column('tasks', sa.Column('deleted', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('tasks', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))

    # Add indexes for new fields
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_deleted', 'tasks', ['deleted'])
    op.create_index('idx_tasks_user_status', 'tasks', ['user_id', 'status'])

    # Add check constraint for status values
    op.create_check_constraint(
        'check_task_status',
        'tasks',
        "status IN ('todo', 'in_progress', 'review', 'done', 'blocked')"
    )


def downgrade() -> None:
    # Drop check constraint
    op.drop_constraint('check_task_status', 'tasks', type_='check')

    # Drop indexes
    op.drop_index('idx_tasks_user_status', table_name='tasks')
    op.drop_index('idx_tasks_deleted', table_name='tasks')
    op.drop_index('idx_tasks_status', table_name='tasks')

    # Drop columns
    op.drop_column('tasks', 'deleted_at')
    op.drop_column('tasks', 'deleted')
    op.drop_column('tasks', 'completed_at')
    op.drop_column('tasks', 'status')
