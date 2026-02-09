"""Create task_history table

Revision ID: 008_create_task_history
Revises: 007_create_task_tags
Create Date: 2026-02-09 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_create_task_history'
down_revision = '007_create_task_tags'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create task_history table
    op.create_table(
        'task_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('change_type', sa.String(50), nullable=False),
        sa.Column('old_value', postgresql.JSONB, nullable=True),
        sa.Column('new_value', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

    # Create indexes
    op.create_index('idx_task_history_task_id', 'task_history', ['task_id'])
    op.create_index('idx_task_history_created_at', 'task_history', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_task_history_created_at', table_name='task_history')
    op.drop_index('idx_task_history_task_id', table_name='task_history')

    # Drop table
    op.drop_table('task_history')
