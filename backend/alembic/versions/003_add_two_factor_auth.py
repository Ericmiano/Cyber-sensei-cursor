"""Add two-factor authentication tables

Revision ID: 003
Revises: 002
Create Date: 2024-12-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create two_factor_auth table
    op.create_table(
        'two_factor_auth',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('secret', sa.String(length=32), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('backup_codes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_two_factor_auth_user_id', 'two_factor_auth', ['user_id'])
    
    # Create two_factor_backup_codes table
    op.create_table(
        'two_factor_backup_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code_hash', sa.String(length=64), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_two_factor_backup_codes_user_id', 'two_factor_backup_codes', ['user_id'])
    op.create_index('ix_two_factor_backup_codes_is_used', 'two_factor_backup_codes', ['is_used'])


def downgrade() -> None:
    op.drop_index('ix_two_factor_backup_codes_is_used', table_name='two_factor_backup_codes')
    op.drop_index('ix_two_factor_backup_codes_user_id', table_name='two_factor_backup_codes')
    op.drop_table('two_factor_backup_codes')
    
    op.drop_index('ix_two_factor_auth_user_id', table_name='two_factor_auth')
    op.drop_table('two_factor_auth')
