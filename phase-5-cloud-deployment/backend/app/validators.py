"""
Validation Utilities for Phase V Backend

Provides common validation functions for API inputs.
"""

import re
from typing import List, Optional
from datetime import datetime


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class Validator:
    """Common validation utilities."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength.

        Requirements:
        - At least 8 characters
        - Contains uppercase letter
        - Contains lowercase letter
        - Contains digit
        - Contains special character

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"

        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"

        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"

        return True, None

    @staticmethod
    def validate_tags(tags: List[str]) -> tuple[bool, Optional[str]]:
        """
        Validate tags list.

        Args:
            tags: List of tags to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not tags:
            return True, None

        if len(tags) > 10:
            return False, "Maximum 10 tags allowed"

        for tag in tags:
            if not tag or not tag.strip():
                return False, "Tags cannot be empty"

            if len(tag) > 50:
                return False, "Tag length cannot exceed 50 characters"

            if not re.match(r'^[a-zA-Z0-9\-_]+$', tag):
                return False, "Tags can only contain letters, numbers, hyphens, and underscores"

        return True, None

    @staticmethod
    def validate_priority(priority: str) -> bool:
        """
        Validate priority value.

        Args:
            priority: Priority value to validate

        Returns:
            True if valid, False otherwise
        """
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        return priority.lower() in valid_priorities

    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> tuple[bool, Optional[str]]:
        """
        Validate date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Tuple of (is_valid, error_message)
        """
        if start_date > end_date:
            return False, "Start date must be before end date"

        return True, None

    @staticmethod
    def validate_reminder_offsets(offsets: List[int]) -> tuple[bool, Optional[str]]:
        """
        Validate reminder offsets.

        Args:
            offsets: List of reminder offsets in minutes

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not offsets:
            return True, None

        if len(offsets) > 5:
            return False, "Maximum 5 reminders allowed"

        for offset in offsets:
            if offset <= 0:
                return False, "Reminder offsets must be positive"

            if offset > 43200:  # 30 days in minutes
                return False, "Reminder offset cannot exceed 30 days"

        return True, None

    @staticmethod
    def validate_recurrence_interval(interval: int) -> tuple[bool, Optional[str]]:
        """
        Validate recurrence interval.

        Args:
            interval: Recurrence interval

        Returns:
            Tuple of (is_valid, error_message)
        """
        if interval < 1:
            return False, "Interval must be at least 1"

        if interval > 1000:
            return False, "Interval cannot exceed 1000"

        return True, None

    @staticmethod
    def validate_days_of_week(days: List[int]) -> tuple[bool, Optional[str]]:
        """
        Validate days of week.

        Args:
            days: List of days (0=Monday, 6=Sunday)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not days:
            return False, "At least one day must be specified"

        if not all(0 <= day <= 6 for day in days):
            return False, "Days must be between 0 (Monday) and 6 (Sunday)"

        if len(days) != len(set(days)):
            return False, "Duplicate days not allowed"

        return True, None

    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """
        Sanitize string input.

        Args:
            text: Text to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Remove leading/trailing whitespace
        text = text.strip()

        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]

        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')

        return text
