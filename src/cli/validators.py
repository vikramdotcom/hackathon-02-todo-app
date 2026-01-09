"""
Input validation utilities for Phase I CLI Todo App.

This module provides validation functions for user input including
ID validation, priority validation, and date parsing.
"""

from datetime import datetime
from typing import Optional


def validate_id(id_input: str) -> int:
    """
    Validate and convert todo ID input.

    Args:
        id_input: User input string for todo ID

    Returns:
        int: Validated todo ID

    Raises:
        ValueError: If ID is not a valid positive integer
    """
    try:
        todo_id = int(id_input)
        if todo_id <= 0:
            raise ValueError("Todo ID must be a positive integer")
        return todo_id
    except ValueError:
        raise ValueError("Todo ID must be a valid number")


def validate_priority(priority_input: str) -> str:
    """
    Validate and normalize priority input.

    Args:
        priority_input: User input string for priority

    Returns:
        str: Normalized priority ("low", "medium", or "high")

    Raises:
        ValueError: If priority is not valid
    """
    priority = priority_input.strip().lower()
    if priority not in ("low", "medium", "high", ""):
        raise ValueError("Priority must be 'low', 'medium', or 'high'")
    return priority if priority else "medium"


def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse date string in multiple formats.

    Accepts:
    - ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS
    - US format: MM/DD/YYYY
    - Alternative: MM-DD-YYYY

    Args:
        date_string: User input string for date

    Returns:
        datetime object if parsing succeeds, None if empty string

    Raises:
        ValueError: If date format is invalid
    """
    if not date_string or not date_string.strip():
        return None

    date_string = date_string.strip()

    # Try ISO 8601 format first
    for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    # Try US format MM/DD/YYYY
    try:
        return datetime.strptime(date_string, "%m/%d/%Y")
    except ValueError:
        pass

    # Try alternative format MM-DD-YYYY
    try:
        return datetime.strptime(date_string, "%m-%d-%Y")
    except ValueError:
        pass

    raise ValueError("Invalid date format. Please use YYYY-MM-DD or MM/DD/YYYY")


def format_date(date: Optional[datetime]) -> str:
    """
    Format datetime object to ISO 8601 string for display.

    Args:
        date: datetime object or None

    Returns:
        str: ISO 8601 formatted date string or "None"
    """
    if date is None:
        return "None"
    return date.strftime("%Y-%m-%d")
