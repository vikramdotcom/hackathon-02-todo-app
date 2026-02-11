"""
Recurrence Service

Handles recurring task logic including:
- Calculating next occurrence dates
- Creating new task instances when recurring tasks are completed
- Managing recurrence patterns and end conditions
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select
from app.models.recurrence import RecurrencePattern, RecurrenceFrequency, RecurrenceEndCondition
from app.models.todo import Todo
import logging

logger = logging.getLogger(__name__)


class RecurrenceService:
    """Service for managing recurring task operations."""

    def __init__(self, db_session: Session):
        """
        Initialize RecurrenceService.

        Args:
            db_session: Database session for operations
        """
        self.db = db_session

    def create_recurrence_pattern(
        self,
        frequency: RecurrenceFrequency,
        interval: int = 1,
        end_condition: RecurrenceEndCondition = RecurrenceEndCondition.NEVER,
        end_after_occurrences: Optional[int] = None,
        end_by_date: Optional[datetime] = None,
        days_of_week: Optional[list[int]] = None,
        day_of_month: Optional[int] = None,
        month_of_year: Optional[int] = None,
        start_date: Optional[datetime] = None
    ) -> RecurrencePattern:
        """
        Create a new recurrence pattern.

        Args:
            frequency: How often the task repeats
            interval: Multiplier for frequency (e.g., every 2 weeks)
            end_condition: When to stop creating instances
            end_after_occurrences: Number of occurrences before stopping
            end_by_date: Date to stop creating instances
            days_of_week: For weekly recurrence, which days (0=Monday, 6=Sunday)
            day_of_month: For monthly recurrence, which day (1-31)
            month_of_year: For yearly recurrence, which month (1-12)
            start_date: When to start the recurrence (defaults to now)

        Returns:
            Created RecurrencePattern instance
        """
        # Calculate first occurrence
        next_occurrence = start_date or datetime.utcnow()

        pattern = RecurrencePattern(
            frequency=frequency,
            interval=interval,
            end_condition=end_condition,
            end_after_occurrences=end_after_occurrences,
            end_by_date=end_by_date,
            next_occurrence=next_occurrence,
            occurrence_count=0,
            days_of_week=days_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year
        )

        self.db.add(pattern)
        self.db.commit()
        self.db.refresh(pattern)

        logger.info(f"Created recurrence pattern {pattern.id} with frequency {frequency}")
        return pattern

    def should_create_next_instance(self, pattern: RecurrencePattern) -> bool:
        """
        Check if a new instance should be created based on end condition.

        Args:
            pattern: RecurrencePattern to check

        Returns:
            True if a new instance should be created, False otherwise
        """
        return pattern.should_create_next_occurrence()

    def calculate_next_occurrence(
        self,
        pattern: RecurrencePattern,
        from_date: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate the next occurrence date for a recurrence pattern.

        Args:
            pattern: RecurrencePattern to calculate from
            from_date: Date to calculate from (defaults to pattern.next_occurrence)

        Returns:
            Next occurrence datetime
        """
        return pattern.calculate_next_occurrence(from_date)

    def create_next_instance(
        self,
        completed_todo: Todo,
        pattern: RecurrencePattern
    ) -> Optional[Todo]:
        """
        Create the next instance of a recurring task after completion.

        Args:
            completed_todo: The completed todo with recurrence
            pattern: The recurrence pattern

        Returns:
            New Todo instance if created, None if recurrence ended
        """
        # Check if we should create next instance
        if not self.should_create_next_instance(pattern):
            logger.info(f"Recurrence pattern {pattern.id} has ended, not creating next instance")
            return None

        # Calculate next occurrence
        next_date = self.calculate_next_occurrence(pattern)

        # Create new todo instance
        new_todo = Todo(
            title=completed_todo.title,
            description=completed_todo.description,
            user_id=completed_todo.user_id,
            priority=completed_todo.priority,
            tags=completed_todo.tags,
            due_date=next_date if completed_todo.due_date else None,
            recurrence_pattern_id=pattern.id,
            completed=False
        )

        self.db.add(new_todo)

        # Update pattern
        pattern.next_occurrence = next_date
        pattern.occurrence_count += 1
        pattern.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(new_todo)

        logger.info(
            f"Created next instance of recurring task: "
            f"todo_id={new_todo.id}, next_occurrence={next_date}, "
            f"occurrence_count={pattern.occurrence_count}"
        )

        return new_todo

    def update_recurrence_pattern(
        self,
        pattern_id: int,
        **updates
    ) -> RecurrencePattern:
        """
        Update a recurrence pattern.

        Args:
            pattern_id: ID of pattern to update
            **updates: Fields to update

        Returns:
            Updated RecurrencePattern instance
        """
        pattern = self.db.get(RecurrencePattern, pattern_id)
        if not pattern:
            raise ValueError(f"Recurrence pattern {pattern_id} not found")

        # Update fields
        for key, value in updates.items():
            if hasattr(pattern, key):
                setattr(pattern, key, value)

        pattern.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(pattern)

        logger.info(f"Updated recurrence pattern {pattern_id}")
        return pattern

    def delete_recurrence_pattern(self, pattern_id: int) -> bool:
        """
        Delete a recurrence pattern.

        Args:
            pattern_id: ID of pattern to delete

        Returns:
            True if deleted, False if not found
        """
        pattern = self.db.get(RecurrencePattern, pattern_id)
        if not pattern:
            return False

        self.db.delete(pattern)
        self.db.commit()

        logger.info(f"Deleted recurrence pattern {pattern_id}")
        return True

    def get_active_patterns(self) -> list[RecurrencePattern]:
        """
        Get all active recurrence patterns that haven't ended.

        Returns:
            List of active RecurrencePattern instances
        """
        statement = select(RecurrencePattern).where(
            RecurrencePattern.next_occurrence <= datetime.utcnow()
        )

        patterns = self.db.exec(statement).all()

        # Filter by end condition
        active_patterns = [
            p for p in patterns
            if p.should_create_next_occurrence()
        ]

        return active_patterns
