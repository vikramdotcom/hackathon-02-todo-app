"""
Todo domain model for Phase I CLI Todo App.

This module defines the canonical Todo entity with validation rules.
The Todo schema is immutable across all phases.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Todo:
    """
    Canonical Todo entity. Immutable across all phases.

    Immutable fields: id, created_at
    Editable fields: title, description, completed, priority, tags, due_date, recurrence, updated_at
    """
    id: int
    title: str
    description: str = ""
    completed: bool = False
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate fields after initialization."""
        self._validate_title()
        self._validate_priority()
        self._validate_description()

    def _validate_title(self):
        """
        Validate title field.

        Rules:
        - Required field (cannot be empty or None)
        - Minimum length: 1 character
        - Maximum length: 10,000 characters
        - Whitespace-only titles are invalid

        Raises:
            ValueError: If title validation fails
        """
        if not self.title or not self.title.strip():
            raise ValueError("Title is required and cannot be empty")
        if len(self.title) > 10000:
            raise ValueError("Title cannot exceed 10,000 characters")

    def _validate_priority(self):
        """
        Validate priority field.

        Rules:
        - Must be one of: "low", "medium", "high"
        - Case-sensitive (lowercase only)

        Raises:
            ValueError: If priority is not valid
        """
        if self.priority not in ("low", "medium", "high"):
            raise ValueError(f"Priority must be 'low', 'medium', or 'high', got '{self.priority}'")

    def _validate_description(self):
        """
        Validate description field.

        Rules:
        - Optional field (can be empty string)
        - Maximum length: 10,000 characters

        Raises:
            ValueError: If description exceeds maximum length
        """
        if len(self.description) > 10000:
            raise ValueError("Description cannot exceed 10,000 characters")
