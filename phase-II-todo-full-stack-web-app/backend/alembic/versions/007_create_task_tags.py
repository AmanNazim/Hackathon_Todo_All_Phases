"""Create task_tags table

Revision ID: 007_create_task_tags
Revises: 006_add_task_status_fields
Create Date: 2026-02-09 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_create_task_tags'
down_revision = '006_add_task_status_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create task_tags table
    op.create_table(
        'task_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('task_id', 'tag', name='uq_task_tag')
    )

    # Create indexes
    op.create_index('idx_task_tags_task_id', 'task_tags', ['task_id'])
    op.create_index('idx_task_tags_tag', 'task_tags', ['tag'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_task_tags_tag', table_name='task_tags')
    op.drop_index('idx_task_tags_task_id', table_name='task_tags')

    # Drop table
    op.drop_table('task_tags')
