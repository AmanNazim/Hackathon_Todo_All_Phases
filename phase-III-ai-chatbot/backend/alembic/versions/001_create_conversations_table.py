"""create conversations table

Revision ID: 001_conversations
Revises:
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '001_conversations'
down_revision = None  # First migration for Phase III
branch_labels = None
depends_on = None


def upgrade():
    """Create conversations table with indexes and constraints"""
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("status IN ('active', 'archived')", name='chk_conversation_status')
    )

    # Create indexes
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index(
        'idx_conversations_updated_at',
        'conversations',
        ['updated_at'],
        postgresql_using='btree',
        postgresql_ops={'updated_at': 'DESC'}
    )
    op.create_index('idx_conversations_user_status', 'conversations', ['user_id', 'status'])


def downgrade():
    """Drop conversations table and indexes"""
    op.drop_index('idx_conversations_user_status', table_name='conversations')
    op.drop_index('idx_conversations_updated_at', table_name='conversations')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
