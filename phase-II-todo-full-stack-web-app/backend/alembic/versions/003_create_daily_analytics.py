"""Create daily_analytics table for analytics aggregation

Revision ID: 003_create_daily_analytics
Revises: 002_auth_features
Create Date: 2026-02-09 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_create_daily_analytics'
down_revision = '002_auth_features'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create daily_analytics table
    op.create_table(
        'daily_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('tasks_created', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tasks_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tasks_deleted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completion_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'date', name='uq_daily_analytics_user_date')
    )

    # Create indexes for daily_analytics table
    op.create_index('idx_daily_analytics_user_id', 'daily_analytics', ['user_id'])
    op.create_index('idx_daily_analytics_date', 'daily_analytics', ['date'])
    op.create_index('idx_daily_analytics_user_date', 'daily_analytics', ['user_id', 'date'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_daily_analytics_user_date', table_name='daily_analytics')
    op.drop_index('idx_daily_analytics_date', table_name='daily_analytics')
    op.drop_index('idx_daily_analytics_user_id', table_name='daily_analytics')

    # Drop daily_analytics table
    op.drop_table('daily_analytics')
