"""
Pydantic Schemas for Phase V API v2

Request and response models for todos and recurrence patterns.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from app.models.todo import TodoPriority
from app.models.recurrence import RecurrenceFrequency, RecurrenceEndCondition


# ============================================================================
# Recurrence Pattern Schemas
# ============================================================================

class RecurrencePatternCreate(BaseModel):
    """Request schema for creating a recurrence pattern."""

    frequency: RecurrenceFrequency = Field(..., description="How often the task repeats")
    interval: int = Field(default=1, ge=1, le=1000, description="Multiplier for frequency")
    end_condition: RecurrenceEndCondition = Field(
        default=RecurrenceEndCondition.NEVER,
        description="When to stop creating instances"
    )
    end_after_occurrences: Optional[int] = Field(
        default=None,
        ge=1,
        le=1000,
        description="Number of occurrences before stopping"
    )
    end_by_date: Optional[datetime] = Field(
        default=None,
        description="Date to stop creating instances"
    )
    days_of_week: Optional[List[int]] = Field(
        default=None,
        description="For weekly recurrence, which days (0=Monday, 6=Sunday)"
    )
    day_of_month: Optional[int] = Field(
        default=None,
        ge=1,
        le=31,
        description="For monthly recurrence, which day"
    )
    month_of_year: Optional[int] = Field(
        default=None,
        ge=1,
        le=12,
        description="For yearly recurrence, which month"
    )
    start_date: Optional[datetime] = Field(
        default=None,
        description="When to start the recurrence (defaults to now)"
    )

    @validator('end_after_occurrences')
    def validate_end_after_occurrences(cls, v, values):
        """Validate end_after_occurrences is set when needed."""
        if values.get('end_condition') == RecurrenceEndCondition.AFTER_OCCURRENCES and v is None:
            raise ValueError("end_after_occurrences required when end_condition is after_occurrences")
        return v

    @validator('end_by_date')
    def validate_end_by_date(cls, v, values):
        """Validate end_by_date is set when needed."""
        if values.get('end_condition') == RecurrenceEndCondition.BY_DATE and v is None:
            raise ValueError("end_by_date required when end_condition is by_date")
        return v

    @validator('days_of_week')
    def validate_days_of_week(cls, v):
        """Validate days of week are in range 0-6."""
        if v is not None:
            if not all(0 <= day <= 6 for day in v):
                raise ValueError("Days of week must be between 0 (Monday) and 6 (Sunday)")
            if len(v) == 0:
                raise ValueError("At least one day must be specified")
        return v


class RecurrencePatternUpdate(BaseModel):
    """Request schema for updating a recurrence pattern."""

    interval: Optional[int] = Field(default=None, ge=1, le=1000)
    end_condition: Optional[RecurrenceEndCondition] = None
    end_after_occurrences: Optional[int] = Field(default=None, ge=1, le=1000)
    end_by_date: Optional[datetime] = None


class RecurrencePatternResponse(BaseModel):
    """Response schema for recurrence pattern."""

    id: int
    frequency: RecurrenceFrequency
    interval: int
    end_condition: RecurrenceEndCondition
    end_after_occurrences: Optional[int]
    end_by_date: Optional[datetime]
    next_occurrence: datetime
    occurrence_count: int
    days_of_week: Optional[List[int]]
    day_of_month: Optional[int]
    month_of_year: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Todo Schemas (Phase V Extended)
# ============================================================================

class TodoCreate(BaseModel):
    """Request schema for creating a todo with Phase V fields."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(default=None, max_length=2000, description="Task description")
    due_date: Optional[datetime] = Field(default=None, description="When the task is due")
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM, description="Task priority")
    tags: Optional[List[str]] = Field(default=None, description="Tags for categorization")
    recurrence_pattern_id: Optional[int] = Field(
        default=None,
        description="Link to recurrence pattern if recurring"
    )
    reminder_offsets: Optional[List[int]] = Field(
        default=None,
        description="Reminder offsets in minutes before due date"
    )

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags are not empty strings."""
        if v is not None:
            v = [tag.strip() for tag in v if tag.strip()]
            if len(v) == 0:
                return None
        return v

    @validator('reminder_offsets')
    def validate_reminder_offsets(cls, v, values):
        """Validate reminder offsets are positive and due_date is set."""
        if v is not None:
            if not all(offset > 0 for offset in v):
                raise ValueError("Reminder offsets must be positive")
            if values.get('due_date') is None:
                raise ValueError("due_date required when reminder_offsets are set")
        return v


class TodoUpdate(BaseModel):
    """Request schema for updating a todo."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[TodoPriority] = None
    tags: Optional[List[str]] = None
    reminder_offsets: Optional[List[int]] = None


class TodoResponse(BaseModel):
    """Response schema for todo with Phase V fields."""

    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    user_id: int

    # Phase V fields
    due_date: Optional[datetime]
    priority: TodoPriority
    tags: Optional[List[str]]
    recurrence_pattern_id: Optional[int]
    reminder_offsets: Optional[List[int]]

    # Computed fields
    is_overdue: bool = Field(description="Whether the task is overdue")
    is_recurring: bool = Field(description="Whether the task is recurring")
    has_reminders: bool = Field(description="Whether the task has reminders")

    class Config:
        from_attributes = True

    @classmethod
    def from_todo(cls, todo):
        """Create response from Todo model instance."""
        return cls(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            created_at=todo.created_at,
            updated_at=todo.updated_at,
            user_id=todo.user_id,
            due_date=todo.due_date,
            priority=todo.priority,
            tags=todo.tags,
            recurrence_pattern_id=todo.recurrence_pattern_id,
            reminder_offsets=todo.reminder_offsets,
            is_overdue=todo.is_overdue(),
            is_recurring=todo.is_recurring(),
            has_reminders=todo.has_reminders()
        )


class TodoListResponse(BaseModel):
    """Response schema for paginated todo list."""

    todos: List[TodoResponse]
    total: int
    limit: int
    offset: int


class TodoSearchRequest(BaseModel):
    """Request schema for searching todos."""

    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum results")


# ============================================================================
# Combined Schemas (Todo + Recurrence Pattern)
# ============================================================================

class RecurringTodoCreate(BaseModel):
    """Request schema for creating a recurring todo with inline pattern."""

    todo: TodoCreate
    recurrence_pattern: RecurrencePatternCreate


class RecurringTodoResponse(BaseModel):
    """Response schema for recurring todo with pattern details."""

    todo: TodoResponse
    recurrence_pattern: RecurrencePatternResponse


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")
