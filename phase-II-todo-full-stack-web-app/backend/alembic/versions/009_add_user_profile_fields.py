"""Add user profile fields to users table

Revision ID: 009_add_user_profile_fields
Revises: 008_create_task_history
Create Date: 2026-02-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009_add_user_profile_fields'
down_revision = '008_create_task_history'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add profile fields to users table
    op.add_column('users', sa.Column('display_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('avatar_thumbnail_url', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))

    # Add indexes for profile queries
    op.create_index('idx_users_display_name', 'users', ['display_name'])


def downgrade() -> None:
    # Drop index
    op.drop_index('idx_users_display_name', table_name='users')

    # Drop columns
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'avatar_thumbnail_url')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'display_name')
