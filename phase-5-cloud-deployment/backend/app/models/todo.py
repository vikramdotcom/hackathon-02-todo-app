"""
Extended Todo Model for Phase V

Adds advanced features: recurring tasks, due dates, reminders, priorities, tags.
Maintains backward compatibility with Phase I-IV schema.
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from enum import Enum


class TodoPriority(str, Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Todo(SQLModel, table=True):
    """
    Extended Todo model with Phase V advanced features.

    Phase I-IV Fields (preserved):
        id: Unique identifier
        title: Task title (required)
        description: Task description (optional)
        completed: Completion status
        created_at: Creation timestamp
        updated_at: Last update timestamp
        user_id: Owner user ID

    Phase V Extensions (new):
        due_date: When the task is due (optional)
        priority: Task priority level (low/medium/high/urgent)
        tags: Array of tags for categorization
        recurrence_pattern_id: Link to recurrence pattern (if recurring)
        reminder_offsets: Array of reminder offsets in minutes before due date
    """

    __tablename__ = "todos"

    # Phase I-IV fields (preserved for backward compatibility)
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="users.id", index=True)

    # Phase V extensions (new fields)
    due_date: Optional[datetime] = Field(default=None, index=True)
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM, index=True)
    tags: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    recurrence_pattern_id: Optional[int] = Field(
        default=None,
        foreign_key="recurrence_patterns.id",
        index=True
    )
    reminder_offsets: Optional[list[int]] = Field(
        default=None,
        sa_column=Column(JSON)
    )  # Minutes before due_date

    # Relationships
    recurrence_pattern: Optional["RecurrencePattern"] = Relationship(back_populates="todos")

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date or self.completed:
            return False
        return datetime.utcnow() > self.due_date

    def is_recurring(self) -> bool:
        """Check if task is recurring."""
        return self.recurrence_pattern_id is not None

    def has_reminders(self) -> bool:
        """Check if task has reminders configured."""
        return bool(self.reminder_offsets and self.due_date)

    def get_reminder_times(self) -> list[datetime]:
        """
        Calculate reminder trigger times based on due date and offsets.

        Returns:
            List of datetime objects when reminders should trigger
        """
        if not self.has_reminders():
            return []

        reminder_times = []
        for offset_minutes in self.reminder_offsets:
            reminder_time = self.due_date - timedelta(minutes=offset_minutes)
            # Only include future reminders
            if reminder_time > datetime.utcnow():
                reminder_times.append(reminder_time)

        return sorted(reminder_times)

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Weekly team standup",
                "description": "Discuss progress and blockers",
                "completed": False,
                "due_date": "2026-02-17T09:00:00Z",
                "priority": "high",
                "tags": ["work", "meetings", "team"],
                "recurrence_pattern_id": 1,
                "reminder_offsets": [1440, 60, 10],  # 1 day, 1 hour, 10 min before
                "user_id": 1
            }
        }
