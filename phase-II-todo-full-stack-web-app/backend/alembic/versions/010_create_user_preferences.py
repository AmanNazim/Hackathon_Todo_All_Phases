"""Create user preferences table

Revision ID: 010_create_user_preferences
Revises: 009_add_user_profile_fields
Create Date: 2026-02-09 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010_create_user_preferences'
down_revision = '009_add_user_profile_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('theme', sa.String(20), nullable=False, server_default='system'),
        sa.Column('language', sa.String(10), nullable=False, server_default='en'),
        sa.Column('notifications', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('privacy', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Create indexes
    op.create_index('idx_user_preferences_user_id', 'user_preferences', ['user_id'])

    # Add check constraint for theme values
    op.create_check_constraint(
        'check_theme_values',
        'user_preferences',
        "theme IN ('light', 'dark', 'system')"
    )


def downgrade() -> None:
    # Drop check constraint
    op.drop_constraint('check_theme_values', 'user_preferences', type_='check')

    # Drop index
    op.drop_index('idx_user_preferences_user_id', table_name='user_preferences')

    # Drop table
    op.drop_table('user_preferences')
