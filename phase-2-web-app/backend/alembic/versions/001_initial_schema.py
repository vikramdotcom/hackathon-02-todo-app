"""Initial schema with users and todos tables

Revision ID: 001
Revises:
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create unique indexes for users
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_username', 'users', ['username'], unique=True)

    # Create check constraints for users
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT chk_email_format
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
    """)

    op.execute("""
        ALTER TABLE users ADD CONSTRAINT chk_username_length
        CHECK (LENGTH(username) >= 3 AND LENGTH(username) <= 50)
    """)

    # Create todos table
    op.create_table(
        'todos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=10000), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('priority', sa.String(length=10), nullable=False, server_default='medium'),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), nullable=False, server_default='{}'),
        sa.Column('due_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('recurrence', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Create indexes for todos
    op.create_index('idx_todos_user_id', 'todos', ['user_id'])
    op.create_index('idx_todos_completed', 'todos', ['completed'])
    op.create_index('idx_todos_priority', 'todos', ['priority'])
    op.create_index('idx_todos_user_completed', 'todos', ['user_id', 'completed'])
    op.create_index('idx_todos_due_date', 'todos', ['due_date'], postgresql_where=sa.text('due_date IS NOT NULL'))
    op.create_index('idx_todos_tags', 'todos', ['tags'], postgresql_using='gin')

    # Create check constraints for todos
    op.execute("""
        ALTER TABLE todos ADD CONSTRAINT chk_priority
        CHECK (priority IN ('low', 'medium', 'high'))
    """)

    op.execute("""
        ALTER TABLE todos ADD CONSTRAINT chk_title_length
        CHECK (LENGTH(title) >= 1 AND LENGTH(title) <= 10000)
    """)

    op.execute("""
        ALTER TABLE todos ADD CONSTRAINT chk_description_length
        CHECK (LENGTH(description) <= 10000)
    """)

    # Create trigger function for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Create triggers for updated_at
    op.execute("""
        CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
        CREATE TRIGGER update_todos_updated_at BEFORE UPDATE ON todos
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute('DROP TRIGGER IF EXISTS update_todos_updated_at ON todos')
    op.execute('DROP TRIGGER IF EXISTS update_users_updated_at ON users')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')

    # Drop todos table
    op.drop_index('idx_todos_tags', table_name='todos')
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
