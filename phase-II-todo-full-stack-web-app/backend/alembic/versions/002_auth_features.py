"""Add authentication features: email verification and password reset

Revision ID: 002_auth_features
Revises: 001_initial_schema
Create Date: 2026-02-09 04:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_auth_features'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add email_verified column to users table
    op.add_column(
        'users',
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false')
    )

    # Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for password_reset_tokens table
    op.create_index('idx_password_reset_tokens_user_id', 'password_reset_tokens', ['user_id'])
    op.create_index('idx_password_reset_tokens_expires_at', 'password_reset_tokens', ['expires_at'])
    op.create_index('idx_password_reset_tokens_token_hash', 'password_reset_tokens', ['token_hash'])

    # Create email_verification_tokens table
    op.create_table(
        'email_verification_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for email_verification_tokens table
    op.create_index('idx_email_verification_tokens_user_id', 'email_verification_tokens', ['user_id'])
    op.create_index('idx_email_verification_tokens_expires_at', 'email_verification_tokens', ['expires_at'])
    op.create_index('idx_email_verification_tokens_token_hash', 'email_verification_tokens', ['token_hash'])


def downgrade() -> None:
    # Drop email_verification_tokens indexes
    op.drop_index('idx_email_verification_tokens_token_hash', table_name='email_verification_tokens')
    op.drop_index('idx_email_verification_tokens_expires_at', table_name='email_verification_tokens')
    op.drop_index('idx_email_verification_tokens_user_id', table_name='email_verification_tokens')

    # Drop email_verification_tokens table
    op.drop_table('email_verification_tokens')

    # Drop password_reset_tokens indexes
    op.drop_index('idx_password_reset_tokens_token_hash', table_name='password_reset_tokens')
    op.drop_index('idx_password_reset_tokens_expires_at', table_name='password_reset_tokens')
    op.drop_index('idx_password_reset_tokens_user_id', table_name='password_reset_tokens')

    # Drop password_reset_tokens table
    op.drop_table('password_reset_tokens')

    # Remove email_verified column from users table
    op.drop_column('users', 'email_verified')
