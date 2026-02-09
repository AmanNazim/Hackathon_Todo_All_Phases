"""Create analytics_cache table for caching analytics metrics

Revision ID: 004_create_analytics_cache
Revises: 003_create_daily_analytics
Create Date: 2026-02-09 05:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_create_analytics_cache'
down_revision = '003_create_daily_analytics'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create analytics_cache table
    op.create_table(
        'analytics_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('metric_value', postgresql.JSONB(), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'metric_name', name='uq_analytics_cache_user_metric')
    )

    # Create indexes for analytics_cache table
    op.create_index('idx_analytics_cache_user_id', 'analytics_cache', ['user_id'])
    op.create_index('idx_analytics_cache_metric_name', 'analytics_cache', ['metric_name'])
    op.create_index('idx_analytics_cache_expires_at', 'analytics_cache', ['expires_at'])
    op.create_index('idx_analytics_cache_user_metric', 'analytics_cache', ['user_id', 'metric_name'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_analytics_cache_user_metric', table_name='analytics_cache')
    op.drop_index('idx_analytics_cache_expires_at', table_name='analytics_cache')
    op.drop_index('idx_analytics_cache_metric_name', table_name='analytics_cache')
    op.drop_index('idx_analytics_cache_user_id', table_name='analytics_cache')

    # Drop analytics_cache table
    op.drop_table('analytics_cache')
