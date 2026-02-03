"""Initial schema with users and todos tables

Revision ID: 001
Revises:
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table with inline constraints (SQLite-compatible)
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        # SQLite supports CHECK constraints in CREATE TABLE, but not ALTER TABLE
        sa.CheckConstraint(
            "LENGTH(username) >= 3 AND LENGTH(username) <= 50",
            name='chk_username_length'
        )
    )

    # Create unique indexes for users
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_username', 'users', ['username'], unique=True)

    # Create todos table with inline constraints (SQLite-compatible)
    op.create_table(
        'todos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=10000), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('priority', sa.String(length=10), nullable=False, server_default='medium'),
        # Use JSON column for tags (SQLite-compatible, works with SQLModel JSON)
        sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('due_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('recurrence', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        # SQLite supports CHECK constraints in CREATE TABLE
        sa.CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name='chk_priority'
        ),
        sa.CheckConstraint(
            "LENGTH(title) >= 1 AND LENGTH(title) <= 10000",
            name='chk_title_length'
        ),
        sa.CheckConstraint(
            "LENGTH(description) <= 10000",
            name='chk_description_length'
        )
    )

    # Create indexes for todos (SQLite-compatible)
    op.create_index('idx_todos_user_id', 'todos', ['user_id'])
    op.create_index('idx_todos_completed', 'todos', ['completed'])
    op.create_index('idx_todos_priority', 'todos', ['priority'])
    op.create_index('idx_todos_user_completed', 'todos', ['user_id', 'completed'])
    # Create index for due_date (regular index works fine for SQLite)
    op.create_index('idx_todos_due_date', 'todos', ['due_date'])


def downgrade() -> None:
    # Drop todos table
    op.drop_index('idx_todos_due_date', table_name='todos')
    op.drop_index('idx_todos_user_completed', table_name='todos')
    op.drop_index('idx_todos_priority', table_name='todos')
    op.drop_index('idx_todos_completed', table_name='todos')
    op.drop_index('idx_todos_user_id', table_name='todos')
    op.drop_table('todos')

    # Drop users table
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
