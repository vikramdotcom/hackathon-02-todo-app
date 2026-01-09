# Data Model: Phase I CLI Todo App

**Feature**: Phase I – In-Memory Python Console Todo App
**Branch**: `001-phase-1-cli-todo`
**Date**: 2026-01-09

## Overview

This document defines the canonical data model for the Todo application. The model is immutable across all five phases and serves as the single source of truth for todo structure and validation rules.

## Entities

### Todo

The core entity representing a single task or action item.

**Schema Definition**:

```python
@dataclass
class Todo:
    """
    Canonical Todo entity. Immutable across all phases.

    Immutable fields: id, created_at
    Editable fields: title, description, completed, priority, tags, due_date, recurrence, updated_at
    """
    id: int                          # Unique auto-increment integer, never reused
    title: str                       # Required, 1-10,000 characters
    description: str                 # Optional, 0-10,000 characters, default ""
    completed: bool                  # Completion status, default False
    priority: str                    # Enum: "low" | "medium" | "high", default "medium"
    tags: List[str]                  # List of tag strings, default []
    due_date: Optional[datetime]     # ISO 8601 datetime or None
    recurrence: Optional[str]        # Recurrence pattern string or None
    created_at: datetime             # Creation timestamp, immutable
    updated_at: datetime             # Last update timestamp, auto-updated on edit
```

**Field Specifications**:

| Field | Type | Required | Mutable | Default | Constraints |
|-------|------|----------|---------|---------|-------------|
| `id` | int | Yes | No | Auto-generated | Unique, auto-increment starting from 1, never reused |
| `title` | str | Yes | Yes | N/A | 1-10,000 characters, non-empty |
| `description` | str | No | Yes | `""` | 0-10,000 characters |
| `completed` | bool | Yes | Yes | `False` | Boolean flag |
| `priority` | str | Yes | Yes | `"medium"` | Enum: `"low"`, `"medium"`, `"high"` |
| `tags` | List[str] | Yes | Yes | `[]` | List of strings, no length limit per tag |
| `due_date` | Optional[datetime] | No | Yes | `None` | ISO 8601 datetime or None |
| `recurrence` | Optional[str] | No | Yes | `None` | Pattern string (e.g., "daily", "weekly") or None |
| `created_at` | datetime | Yes | No | `datetime.now()` | ISO 8601 datetime, set on creation |
| `updated_at` | datetime | Yes | Yes | `datetime.now()` | ISO 8601 datetime, updated on every edit |

**Validation Rules**:

1. **ID Uniqueness**: Each todo must have a unique integer ID. IDs are auto-generated starting from 1 and increment by 1 for each new todo. Deleted todo IDs are never reused.

2. **Title Constraints**:
   - Required field (cannot be empty or None)
   - Minimum length: 1 character
   - Maximum length: 10,000 characters
   - Whitespace-only titles are invalid

3. **Description Constraints**:
   - Optional field (can be empty string or None)
   - Maximum length: 10,000 characters
   - Empty string is valid

4. **Priority Validation**:
   - Must be one of: `"low"`, `"medium"`, `"high"`
   - Case-sensitive (lowercase only)
   - Invalid values rejected with error message

5. **Tags Validation**:
   - List of strings (can be empty list)
   - No duplicate tags within a single todo
   - Tag strings can be any length
   - Tags are case-sensitive

6. **Date/Time Validation**:
   - `due_date`: Must be valid ISO 8601 datetime or None
   - `created_at`: Set automatically on creation, never modified
   - `updated_at`: Set automatically on creation, updated on every edit
   - All datetimes stored as Python `datetime` objects
   - Display format: ISO 8601 string (e.g., "2026-01-09T14:30:00")

7. **Recurrence Validation**:
   - Optional string field (can be None)
   - Phase I stores pattern but does not process it
   - Examples: "daily", "weekly", "monthly", "every 2 weeks"
   - No validation on pattern format in Phase I

**State Transitions**:

```
[New Todo]
    ↓ (create with title)
[Incomplete Todo] (completed=False)
    ↓ (mark complete)
[Completed Todo] (completed=True)
    ↓ (mark incomplete)
[Incomplete Todo] (completed=False)
    ↓ (delete)
[Deleted] (removed from memory)
```

**Invariants**:

1. **ID Immutability**: Once assigned, a todo's ID never changes
2. **Creation Timestamp Immutability**: `created_at` is set once and never modified
3. **Update Timestamp Consistency**: `updated_at` is always >= `created_at`
4. **Priority Enum**: `priority` is always one of the three valid values
5. **Title Non-Empty**: `title` is never empty or None after validation

---

### Session

Represents the current CLI session context. Not persisted; exists only during application runtime.

**Schema Definition**:

```python
@dataclass
class Session:
    """
    Session context for tracking operations and state during CLI execution.
    Not persisted; exists only in memory during runtime.
    """
    todos: List[Todo]                # In-memory list of all todos
    next_id: int                     # Next available ID for new todo
    operations: Dict[str, int]       # Operation counts: {"added": 0, "updated": 0, ...}
```

**Field Specifications**:

| Field | Type | Description |
|-------|------|-------------|
| `todos` | List[Todo] | In-memory list of all todos, initially empty |
| `next_id` | int | Next available ID for new todo, starts at 1 |
| `operations` | Dict[str, int] | Operation counts: `{"added": 0, "updated": 0, "deleted": 0, "completed": 0}` |

**Session Operations**:

- **Initialize**: Create empty session with `todos=[]`, `next_id=1`, `operations={"added": 0, "updated": 0, "deleted": 0, "completed": 0}`
- **Track Operation**: Increment operation count when user performs action
- **Get Summary**: Return current state (total todos, operation counts)
- **Terminate**: Display summary and exit (data is lost)

**Relationships**:

- Session contains zero or more Todos (one-to-many)
- Todos do not reference Session (unidirectional relationship)

---

## Data Flow

### Create Todo Flow

```
User Input (title, optional fields)
    ↓
Validate Input (title required, priority enum, etc.)
    ↓
Generate ID (next_id, increment)
    ↓
Set Timestamps (created_at, updated_at = now())
    ↓
Apply Defaults (description="", priority="medium", tags=[], etc.)
    ↓
Create Todo Object
    ↓
Add to Session.todos
    ↓
Increment Session.operations["added"]
```

### Update Todo Flow

```
User Input (todo ID, fields to update)
    ↓
Validate ID (exists in session)
    ↓
Validate Field Values (priority enum, title length, etc.)
    ↓
Update Fields (preserve id, created_at)
    ↓
Update Timestamp (updated_at = now())
    ↓
Increment Session.operations["updated"]
```

### Delete Todo Flow

```
User Input (todo ID)
    ↓
Validate ID (exists in session)
    ↓
Remove from Session.todos
    ↓
Increment Session.operations["deleted"]
    ↓
(ID is never reused)
```

---

## Phase Compatibility

This data model is designed for forward compatibility across all five phases:

- **Phase I (CLI)**: In-memory storage, full CRUD operations
- **Phase II (Web)**: Same model, add database persistence (SQLite/PostgreSQL)
- **Phase III (AI)**: Same model, AI agent translates natural language to operations
- **Phase IV (Kubernetes)**: Same model, distributed storage with service boundaries
- **Phase V (Cloud)**: Same model, multi-region replication and eventual consistency

**Immutability Guarantee**: The Todo schema (field names, types, constraints) will not change across phases. New fields may be added (e.g., `user_id` in Phase II) but existing fields remain unchanged.

---

## Implementation Notes

### Python Dataclass Implementation

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Todo:
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
        if not self.title or not self.title.strip():
            raise ValueError("Title is required and cannot be empty")
        if len(self.title) > 10000:
            raise ValueError("Title cannot exceed 10,000 characters")

    def _validate_priority(self):
        if self.priority not in ("low", "medium", "high"):
            raise ValueError(f"Priority must be 'low', 'medium', or 'high', got '{self.priority}'")

    def _validate_description(self):
        if len(self.description) > 10000:
            raise ValueError("Description cannot exceed 10,000 characters")
```

### ID Generation Strategy

```python
def generate_next_id(todos: List[Todo]) -> int:
    """Generate next available ID. Never reuse deleted IDs."""
    if not todos:
        return 1
    return max(todo.id for todo in todos) + 1
```

---

## Summary

The Todo data model is the canonical representation of a task in the system. It is immutable across all phases and serves as the contract between layers (Domain, Service, Interface). All validation rules are enforced at the domain layer (Todo class), ensuring data integrity regardless of how the todo is created or modified.
