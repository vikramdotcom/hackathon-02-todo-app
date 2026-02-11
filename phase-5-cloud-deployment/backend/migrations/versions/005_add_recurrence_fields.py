"""Add recurrence fields and patterns table

Revision ID: 005
Revises: 004
Create Date: 2026-02-11

Phase V: Add support for recurring tasks with advanced scheduling.

Changes:
- Create recurrence_patterns table for defining recurrence rules
- Add Phase V fields to todos table: due_date, priority, tags, recurrence_pattern_id, reminder_offsets
- Create indexes for efficient querying
- Maintain backward compatibility with Phase I-IV data
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Apply Phase V schema changes.

    Creates recurrence_patterns table and extends todos table with new fields.
    All new fields are nullable to maintain backward compatibility.
    """

    # Create recurrence_patterns table
    op.create_table(
        'recurrence_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('frequency', sa.String(length=20), nullable=False),
        sa.Column('interval', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('end_condition', sa.String(length=30), nullable=False, server_default='never'),
        sa.Column('end_after_occurrences', sa.Integer(), nullable=True),
        sa.Column('end_by_date', sa.DateTime(), nullable=True),
        sa.Column('next_occurrence', sa.DateTime(), nullable=False),
        sa.Column('occurrence_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_of_week', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('day_of_month', sa.Integer(), nullable=True),
        sa.Column('month_of_year', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes on recurrence_patterns
    op.create_index('ix_recurrence_patterns_frequency', 'recurrence_patterns', ['frequency'])
    op.create_index('ix_recurrence_patterns_next_occurrence', 'recurrence_patterns', ['next_occurrence'])

    # Add Phase V fields to todos table
    op.add_column('todos', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('todos', sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'))
    op.add_column('todos', sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('todos', sa.Column('recurrence_pattern_id', sa.Integer(), nullable=True))
    op.add_column('todos', sa.Column('reminder_offsets', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Create indexes on new todos fields
    op.create_index('ix_todos_due_date', 'todos', ['due_date'])
    op.create_index('ix_todos_priority', 'todos', ['priority'])
    op.create_index('ix_todos_recurrence_pattern_id', 'todos', ['recurrence_pattern_id'])

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_todos_recurrence_pattern_id',
        'todos',
        'recurrence_patterns',
        ['recurrence_pattern_id'],
        ['id'],
        ondelete='SET NULL'  # If pattern is deleted, set todo's recurrence_pattern_id to NULL
    )

    # Add check constraints for data validation
    op.create_check_constraint(
        'ck_recurrence_patterns_interval_positive',
        'recurrence_patterns',
        'interval >= 1 AND interval <= 1000'
    )

    op.create_check_constraint(
        'ck_recurrence_patterns_occurrence_count_non_negative',
        'recurrence_patterns',
        'occurrence_count >= 0'
    )

    op.create_check_constraint(
        'ck_recurrence_patterns_day_of_month_valid',
        'recurrence_patterns',
        'day_of_month IS NULL OR (day_of_month >= 1 AND day_of_month <= 31)'
    )

    op.create_check_constraint(
        'ck_recurrence_patterns_month_of_year_valid',
        'recurrence_patterns',
        'month_of_year IS NULL OR (month_of_year >= 1 AND month_of_year <= 12)'
    )

    op.create_check_constraint(
        'ck_recurrence_patterns_end_after_occurrences_positive',
        'recurrence_patterns',
        'end_after_occurrences IS NULL OR (end_after_occurrences >= 1 AND end_after_occurrences <= 1000)'
    )


def downgrade() -> None:
    """
    Rollback Phase V schema changes.

    WARNING: This will delete all recurrence patterns and remove Phase V fields from todos.
    Data in these fields will be lost.
    """

    # Drop check constraints
    op.drop_constraint('ck_recurrence_patterns_end_after_occurrences_positive', 'recurrence_patterns', type_='check')
    op.drop_constraint('ck_recurrence_patterns_month_of_year_valid', 'recurrence_patterns', type_='check')
    op.drop_constraint('ck_recurrence_patterns_day_of_month_valid', 'recurrence_patterns', type_='check')
    op.drop_constraint('ck_recurrence_patterns_occurrence_count_non_negative', 'recurrence_patterns', type_='check')
    op.drop_constraint('ck_recurrence_patterns_interval_positive', 'recurrence_patterns', type_='check')

    # Drop foreign key constraint
    op.drop_constraint('fk_todos_recurrence_pattern_id', 'todos', type_='foreignkey')

    # Drop indexes on todos
    op.drop_index('ix_todos_recurrence_pattern_id', table_name='todos')
    op.drop_index('ix_todos_priority', table_name='todos')
    op.drop_index('ix_todos_due_date', table_name='todos')

    # Drop Phase V columns from todos
    op.drop_column('todos', 'reminder_offsets')
    op.drop_column('todos', 'recurrence_pattern_id')
    op.drop_column('todos', 'tags')
    op.drop_column('todos', 'priority')
    op.drop_column('todos', 'due_date')

    # Drop indexes on recurrence_patterns
    op.drop_index('ix_recurrence_patterns_next_occurrence', table_name='recurrence_patterns')
    op.drop_index('ix_recurrence_patterns_frequency', table_name='recurrence_patterns')

    # Drop recurrence_patterns table
    op.drop_table('recurrence_patterns')
