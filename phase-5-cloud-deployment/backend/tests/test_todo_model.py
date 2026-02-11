"""
Unit Tests for Todo Model

Tests todo model functionality including:
- Helper methods (is_overdue, is_recurring, has_reminders)
- Reminder time calculations
- Phase V field validation
"""

import pytest
from datetime import datetime, timedelta
from app.models.todo import Todo, TodoPriority


class TestTodoHelperMethods:
    """Test Todo model helper methods."""

    def test_is_overdue_with_past_due_date(self, session, sample_user_id):
        """Test that todo with past due date is marked as overdue."""
        todo = Todo(
            title="Overdue Task",
            user_id=sample_user_id,
            due_date=datetime.utcnow() - timedelta(days=1),
            completed=False
        )
        assert todo.is_overdue() is True

    def test_is_overdue_with_future_due_date(self, session, sample_user_id):
        """Test that todo with future due date is not overdue."""
        todo = Todo(
            title="Future Task",
            user_id=sample_user_id,
            due_date=datetime.utcnow() + timedelta(days=1),
            completed=False
        )
        assert todo.is_overdue() is False

    def test_is_overdue_with_no_due_date(self, session, sample_user_id):
        """Test that todo without due date is not overdue."""
        todo = Todo(
            title="No Due Date",
            user_id=sample_user_id,
            completed=False
        )
        assert todo.is_overdue() is False

    def test_is_overdue_completed_task(self, session, sample_user_id):
        """Test that completed task is not overdue even if past due date."""
        todo = Todo(
            title="Completed Task",
            user_id=sample_user_id,
            due_date=datetime.utcnow() - timedelta(days=1),
            completed=True
        )
        assert todo.is_overdue() is False

    def test_is_recurring_with_pattern(self, session, sample_user_id, sample_recurrence_pattern):
        """Test that todo with recurrence pattern is marked as recurring."""
        todo = Todo(
            title="Recurring Task",
            user_id=sample_user_id,
            recurrence_pattern_id=sample_recurrence_pattern.id
        )
        assert todo.is_recurring() is True

    def test_is_recurring_without_pattern(self, session, sample_user_id):
        """Test that todo without recurrence pattern is not recurring."""
        todo = Todo(
            title="One-time Task",
            user_id=sample_user_id
        )
        assert todo.is_recurring() is False

    def test_has_reminders_with_offsets_and_due_date(self, session, sample_user_id):
        """Test that todo with reminders and due date has reminders."""
        todo = Todo(
            title="Task with Reminders",
            user_id=sample_user_id,
            due_date=datetime.utcnow() + timedelta(days=1),
            reminder_offsets=[60, 1440]
        )
        assert todo.has_reminders() is True

    def test_has_reminders_without_due_date(self, session, sample_user_id):
        """Test that todo without due date has no reminders."""
        todo = Todo(
            title="Task without Due Date",
            user_id=sample_user_id,
            reminder_offsets=[60]
        )
        assert todo.has_reminders() is False

    def test_has_reminders_without_offsets(self, session, sample_user_id):
        """Test that todo without reminder offsets has no reminders."""
        todo = Todo(
            title="Task without Reminders",
            user_id=sample_user_id,
            due_date=datetime.utcnow() + timedelta(days=1)
        )
        assert todo.has_reminders() is False


class TestTodoReminderCalculations:
    """Test reminder time calculations."""

    def test_get_reminder_times_calculates_correctly(self, session, sample_user_id):
        """Test that reminder times are calculated correctly."""
        due_date = datetime.utcnow() + timedelta(days=1)
        todo = Todo(
            title="Task with Reminders",
            user_id=sample_user_id,
            due_date=due_date,
            reminder_offsets=[60, 1440]  # 1 hour and 1 day before
        )
        
        reminder_times = todo.get_reminder_times()
        assert len(reminder_times) == 2
        assert reminder_times[0] == due_date - timedelta(minutes=1440)
        assert reminder_times[1] == due_date - timedelta(minutes=60)

    def test_get_reminder_times_filters_past_reminders(self, session, sample_user_id):
        """Test that past reminder times are filtered out."""
        due_date = datetime.utcnow() + timedelta(hours=2)
        todo = Todo(
            title="Task with Past Reminders",
            user_id=sample_user_id,
            due_date=due_date,
            reminder_offsets=[180, 60]  # 3 hours and 1 hour before
        )
        
        reminder_times = todo.get_reminder_times()
        # Only 1 hour reminder should be included (3 hours is in the past)
        assert len(reminder_times) == 1

    def test_get_reminder_times_returns_empty_without_reminders(self, session, sample_user_id):
        """Test that empty list is returned when no reminders configured."""
        todo = Todo(
            title="Task without Reminders",
            user_id=sample_user_id,
            due_date=datetime.utcnow() + timedelta(days=1)
        )
        
        reminder_times = todo.get_reminder_times()
        assert reminder_times == []


class TestTodoPriority:
    """Test todo priority functionality."""

    def test_default_priority_is_medium(self, session, sample_user_id):
        """Test that default priority is MEDIUM."""
        todo = Todo(
            title="Task",
            user_id=sample_user_id
        )
        assert todo.priority == TodoPriority.MEDIUM

    def test_can_set_all_priority_levels(self, session, sample_user_id):
        """Test that all priority levels can be set."""
        for priority in TodoPriority:
            todo = Todo(
                title=f"Task {priority.value}",
                user_id=sample_user_id,
                priority=priority
            )
            assert todo.priority == priority


class TestTodoTags:
    """Test todo tags functionality."""

    def test_tags_can_be_set(self, session, sample_user_id):
        """Test that tags can be set on todo."""
        tags = ["work", "urgent", "meeting"]
        todo = Todo(
            title="Task with Tags",
            user_id=sample_user_id,
            tags=tags
        )
        assert todo.tags == tags

    def test_tags_default_to_none(self, session, sample_user_id):
        """Test that tags default to None."""
        todo = Todo(
            title="Task without Tags",
            user_id=sample_user_id
        )
        assert todo.tags is None
