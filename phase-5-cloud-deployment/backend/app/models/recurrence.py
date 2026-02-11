"""
Recurrence Pattern Model

Defines how tasks repeat: daily, weekly, monthly, yearly, or custom intervals.
Supports end conditions: never, after N occurrences, or by specific date.
"""

from datetime import datetime, timedelta
from typing import Optional, Literal
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import validator


class RecurrenceFrequency(str, Enum):
    """Frequency options for recurring tasks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class RecurrenceEndCondition(str, Enum):
    """End condition options for recurring tasks."""
    NEVER = "never"
    AFTER_OCCURRENCES = "after_occurrences"
    BY_DATE = "by_date"


class RecurrencePattern(SQLModel, table=True):
    """
    Recurrence pattern for repeating tasks.

    Attributes:
        id: Unique identifier
        frequency: How often the task repeats (daily, weekly, monthly, yearly, custom)
        interval: Multiplier for frequency (e.g., every 2 weeks = interval:2, frequency:weekly)
        end_condition: When to stop creating new instances
        end_after_occurrences: Number of occurrences before stopping (if end_condition is after_occurrences)
        end_by_date: Date to stop creating instances (if end_condition is by_date)
        next_occurrence: Calculated next occurrence date
        occurrence_count: Number of instances created so far
        days_of_week: For weekly recurrence, which days (0=Monday, 6=Sunday)
        day_of_month: For monthly recurrence, which day (1-31)
        month_of_year: For yearly recurrence, which month (1-12)
        created_at: When this pattern was created
        updated_at: When this pattern was last updated
    """

    __tablename__ = "recurrence_patterns"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Frequency configuration
    frequency: RecurrenceFrequency = Field(index=True)
    interval: int = Field(default=1, ge=1, le=1000)  # Every N days/weeks/months/years

    # End condition
    end_condition: RecurrenceEndCondition = Field(default=RecurrenceEndCondition.NEVER)
    end_after_occurrences: Optional[int] = Field(default=None, ge=1, le=1000)
    end_by_date: Optional[datetime] = Field(default=None)

    # Tracking
    next_occurrence: datetime = Field(index=True)
    occurrence_count: int = Field(default=0, ge=0)

    # Advanced scheduling (stored as JSON for flexibility)
    days_of_week: Optional[list[int]] = Field(default=None, sa_column=Column(JSON))  # [0-6] for weekly
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)  # For monthly
    month_of_year: Optional[int] = Field(default=None, ge=1, le=12)  # For yearly

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('days_of_week')
    def validate_days_of_week(cls, v):
        """Validate days of week are in range 0-6."""
        if v is not None:
            if not all(0 <= day <= 6 for day in v):
                raise ValueError("Days of week must be between 0 (Monday) and 6 (Sunday)")
            if len(v) == 0:
                raise ValueError("At least one day must be specified for weekly recurrence")
        return v

    @validator('end_after_occurrences')
    def validate_end_after_occurrences(cls, v, values):
        """Validate end_after_occurrences is set when end_condition is after_occurrences."""
        if values.get('end_condition') == RecurrenceEndCondition.AFTER_OCCURRENCES and v is None:
            raise ValueError("end_after_occurrences must be set when end_condition is after_occurrences")
        return v

    @validator('end_by_date')
    def validate_end_by_date(cls, v, values):
        """Validate end_by_date is set when end_condition is by_date."""
        if values.get('end_condition') == RecurrenceEndCondition.BY_DATE and v is None:
            raise ValueError("end_by_date must be set when end_condition is by_date")
        return v

    def should_create_next_occurrence(self) -> bool:
        """
        Check if a new occurrence should be created based on end condition.

        Returns:
            True if a new occurrence should be created, False otherwise
        """
        if self.end_condition == RecurrenceEndCondition.NEVER:
            return True

        if self.end_condition == RecurrenceEndCondition.AFTER_OCCURRENCES:
            return self.occurrence_count < self.end_after_occurrences

        if self.end_condition == RecurrenceEndCondition.BY_DATE:
            return datetime.utcnow() < self.end_by_date

        return False

    def calculate_next_occurrence(self, from_date: Optional[datetime] = None) -> datetime:
        """
        Calculate the next occurrence date based on frequency and interval.

        Args:
            from_date: Date to calculate from (defaults to next_occurrence)

        Returns:
            Next occurrence datetime
        """
        base_date = from_date or self.next_occurrence

        if self.frequency == RecurrenceFrequency.DAILY:
            return base_date + timedelta(days=self.interval)

        elif self.frequency == RecurrenceFrequency.WEEKLY:
            # Add interval weeks
            next_date = base_date + timedelta(weeks=self.interval)

            # If specific days of week are set, find next matching day
            if self.days_of_week:
                while next_date.weekday() not in self.days_of_week:
                    next_date += timedelta(days=1)

            return next_date

        elif self.frequency == RecurrenceFrequency.MONTHLY:
            # Add interval months
            month = base_date.month + self.interval
            year = base_date.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1

            # Handle day of month
            day = self.day_of_month or base_date.day

            # Handle months with fewer days (e.g., Feb 30 -> Feb 28)
            import calendar
            max_day = calendar.monthrange(year, month)[1]
            day = min(day, max_day)

            return base_date.replace(year=year, month=month, day=day)

        elif self.frequency == RecurrenceFrequency.YEARLY:
            # Add interval years
            year = base_date.year + self.interval
            month = self.month_of_year or base_date.month
            day = self.day_of_month or base_date.day

            # Handle leap year edge case (Feb 29)
            import calendar
            max_day = calendar.monthrange(year, month)[1]
            day = min(day, max_day)

            return base_date.replace(year=year, month=month, day=day)

        else:  # CUSTOM
            # For custom frequency, default to daily interval
            return base_date + timedelta(days=self.interval)

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "frequency": "weekly",
                "interval": 1,
                "end_condition": "never",
                "next_occurrence": "2026-02-18T09:00:00Z",
                "occurrence_count": 5,
                "days_of_week": [0, 2, 4]  # Monday, Wednesday, Friday
            }
        }
