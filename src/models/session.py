"""
Session context for Phase I CLI Todo App.

This module defines the Session entity that tracks the current CLI session state.
"""

from dataclasses import dataclass, field
from typing import List, Dict
from src.models.todo import Todo


@dataclass
class Session:
    """
    Session context for tracking operations and state during CLI execution.
    Not persisted; exists only in memory during runtime.
    """
    todos: List[Todo] = field(default_factory=list)
    next_id: int = 1
    operations: Dict[str, int] = field(default_factory=lambda: {
        "added": 0,
        "updated": 0,
        "deleted": 0,
        "completed": 0
    })

    def __post_init__(self):
        """Initialize session with default values if not provided."""
        if not self.operations:
            self.operations = {
                "added": 0,
                "updated": 0,
                "deleted": 0,
                "completed": 0
            }
