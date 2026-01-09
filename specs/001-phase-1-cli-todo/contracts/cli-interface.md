# CLI Interface Contract: Phase I Todo App

**Feature**: Phase I – In-Memory Python Console Todo App
**Branch**: `001-phase-1-cli-todo`
**Date**: 2026-01-09

## Overview

This document defines the CLI interface contract for the Phase I todo application. It specifies the menu structure, user interaction patterns, input/output formats, and error handling behavior.

## Interface Type

**Type**: Menu-driven CLI (Command Line Interface)
**I/O Protocol**: stdin (input) / stdout (output) / stderr (errors)
**Interaction Model**: Synchronous, blocking, single-threaded

## Main Menu

### Menu Display Format

```
=== Todo Application ===

1. Add Todo
2. View All Todos
3. Update Todo
4. Delete Todo
5. Mark Todo Complete
6. Mark Todo Incomplete
7. Filter Todos
8. Session Summary
9. Exit

Enter your choice (1-9): _
```

### Menu Behavior

- **Display**: Menu is displayed after application launch and after each operation completes
- **Input**: User enters a number (1-9) corresponding to their choice
- **Validation**: Invalid input (non-numeric, out of range) displays error and re-prompts
- **Loop**: Menu loop continues until user selects "Exit" (option 9)

---

## Operation Contracts

### 1. Add Todo

**Menu Option**: 1
**Purpose**: Create a new todo with user-provided details

**Input Prompts**:
```
Enter title (required): _
Enter description (optional, press Enter to skip): _
Enter priority (low/medium/high, default: medium): _
Enter tags (comma-separated, optional): _
Enter due date (YYYY-MM-DD or MM/DD/YYYY, optional): _
Enter recurrence pattern (optional, e.g., 'daily', 'weekly'): _
```

**Input Validation**:
- **Title**: Required, 1-10,000 characters, non-empty after stripping whitespace
- **Description**: Optional, 0-10,000 characters
- **Priority**: Must be "low", "medium", or "high" (case-insensitive, converted to lowercase)
- **Tags**: Comma-separated strings, trimmed, duplicates removed
- **Due Date**: Multiple formats accepted (ISO 8601, MM/DD/YYYY, MM-DD-YYYY), converted to datetime
- **Recurrence**: Free-form string, no validation in Phase I

**Success Output**:
```
✓ Todo created successfully!
  ID: 1
  Title: Buy groceries
  Created: 2026-01-09T14:30:00
```

**Error Output**:
```
✗ Error: Title is required and cannot be empty
  Please try again.
```

**Postconditions**:
- New todo added to session with unique ID
- `created_at` and `updated_at` set to current timestamp
- Session operation count `added` incremented
- Returns to main menu

---

### 2. View All Todos

**Menu Option**: 2
**Purpose**: Display all todos in the current session

**Input**: None (no prompts)

**Output Format** (table):
```
=== All Todos (3 total) ===

ID | Title              | Status    | Priority | Due Date   | Tags
---|--------------------|-----------|-----------|-----------|---------
1  | Buy groceries      | Pending   | high     | 2026-01-10 | shopping
2  | Write report       | Completed | medium   | None       | work
3  | Call dentist       | Pending   | low      | 2026-01-15 | health

Press Enter to continue...
```

**Empty List Output**:
```
=== All Todos (0 total) ===

No todos found. Add your first todo to get started!

Press Enter to continue...
```

**Postconditions**:
- No state changes
- Returns to main menu after user presses Enter

---

### 3. Update Todo

**Menu Option**: 3
**Purpose**: Modify an existing todo's fields

**Input Prompts**:
```
Enter todo ID to update: _
```

**Validation**:
- ID must be numeric
- ID must exist in current session

**If Valid, Display Current Values**:
```
Current todo details:
  ID: 1
  Title: Buy groceries
  Description: Get milk, eggs, bread
  Priority: high
  Tags: shopping
  Due Date: 2026-01-10
  Recurrence: None

Enter new values (press Enter to keep current value):
  Title [Buy groceries]: _
  Description [Get milk, eggs, bread]: _
  Priority [high]: _
  Tags [shopping]: _
  Due Date [2026-01-10]: _
  Recurrence [None]: _
```

**Success Output**:
```
✓ Todo updated successfully!
  ID: 1
  Updated: 2026-01-09T14:35:00
```

**Error Output**:
```
✗ Error: Todo with ID 99 not found
  Please enter a valid todo ID.
```

**Postconditions**:
- Todo fields updated (except `id` and `created_at`)
- `updated_at` set to current timestamp
- Session operation count `updated` incremented
- Returns to main menu

---

### 4. Delete Todo

**Menu Option**: 4
**Purpose**: Remove a todo from the session

**Input Prompts**:
```
Enter todo ID to delete: _
```

**Validation**:
- ID must be numeric
- ID must exist in current session

**Confirmation Prompt**:
```
Are you sure you want to delete this todo?
  ID: 1
  Title: Buy groceries
Confirm (y/n): _
```

**Success Output**:
```
✓ Todo deleted successfully!
  ID: 1
```

**Cancelled Output**:
```
Deletion cancelled.
```

**Error Output**:
```
✗ Error: Todo with ID 99 not found
  Please enter a valid todo ID.
```

**Postconditions**:
- Todo removed from session (if confirmed)
- Session operation count `deleted` incremented (if confirmed)
- ID is never reused
- Returns to main menu

---

### 5. Mark Todo Complete

**Menu Option**: 5
**Purpose**: Set a todo's completed status to True

**Input Prompts**:
```
Enter todo ID to mark complete: _
```

**Validation**:
- ID must be numeric
- ID must exist in current session

**Success Output**:
```
✓ Todo marked as complete!
  ID: 1
  Title: Buy groceries
```

**Already Complete Output**:
```
ℹ Todo is already marked as complete.
  ID: 1
  Title: Buy groceries
```

**Error Output**:
```
✗ Error: Todo with ID 99 not found
  Please enter a valid todo ID.
```

**Postconditions**:
- Todo `completed` field set to True
- `updated_at` set to current timestamp
- Session operation count `completed` incremented
- Returns to main menu

---

### 6. Mark Todo Incomplete

**Menu Option**: 6
**Purpose**: Set a todo's completed status to False

**Input Prompts**:
```
Enter todo ID to mark incomplete: _
```

**Validation**:
- ID must be numeric
- ID must exist in current session

**Success Output**:
```
✓ Todo marked as incomplete!
  ID: 1
  Title: Buy groceries
```

**Already Incomplete Output**:
```
ℹ Todo is already marked as incomplete.
  ID: 1
  Title: Buy groceries
```

**Error Output**:
```
✗ Error: Todo with ID 99 not found
  Please enter a valid todo ID.
```

**Postconditions**:
- Todo `completed` field set to False
- `updated_at` set to current timestamp
- Returns to main menu

---

### 7. Filter Todos

**Menu Option**: 7
**Purpose**: Display todos matching filter criteria

**Filter Menu**:
```
=== Filter Todos ===

1. By Status (Completed/Pending/All)
2. By Priority (High/Medium/Low/All)
3. By Tag
4. Back to Main Menu

Enter your choice (1-4): _
```

**Filter by Status**:
```
Select status:
  1. Completed
  2. Pending
  3. All
Enter choice (1-3): _
```

**Filter by Priority**:
```
Select priority:
  1. High
  2. Medium
  3. Low
  4. All
Enter choice (1-4): _
```

**Filter by Tag**:
```
Enter tag name: _
```

**Output Format**: Same as "View All Todos" but with filtered results

**Empty Results Output**:
```
=== Filtered Todos (0 matches) ===

No todos match the selected filter.

Press Enter to continue...
```

**Postconditions**:
- No state changes
- Returns to filter menu (not main menu) for additional filtering
- User can select "Back to Main Menu" to exit filter mode

---

### 8. Session Summary

**Menu Option**: 8
**Purpose**: Display statistics for the current session

**Output Format**:
```
=== Session Summary ===

Total Todos: 5
  - Completed: 2
  - Pending: 3

Operations This Session:
  - Todos Added: 7
  - Todos Updated: 4
  - Todos Deleted: 2
  - Todos Marked Complete: 3

Press Enter to continue...
```

**Postconditions**:
- No state changes
- Returns to main menu after user presses Enter

---

### 9. Exit

**Menu Option**: 9
**Purpose**: Terminate the application

**Output**:
```
=== Session Summary ===

Total Todos: 5
  - Completed: 2
  - Pending: 3

Operations This Session:
  - Todos Added: 7
  - Todos Updated: 4
  - Todos Deleted: 2
  - Todos Marked Complete: 3

Thank you for using Todo Application!
Goodbye!
```

**Postconditions**:
- Application terminates
- All data is lost (in-memory only)
- Exit code 0 (success)

---

## Error Handling

### Input Validation Errors

**Pattern**: Display error message, re-prompt for input, do not crash

**Examples**:
```
✗ Error: Invalid choice. Please enter a number between 1 and 9.
Enter your choice (1-9): _

✗ Error: Title is required and cannot be empty.
Enter title (required): _

✗ Error: Priority must be 'low', 'medium', or 'high'.
Enter priority (low/medium/high, default: medium): _

✗ Error: Invalid date format. Please use YYYY-MM-DD or MM/DD/YYYY.
Enter due date (YYYY-MM-DD or MM/DD/YYYY, optional): _
```

### System Errors

**Pattern**: Display error message, return to main menu, do not crash

**Examples**:
```
✗ System Error: Unable to read input. Returning to main menu.

✗ System Error: Unexpected error occurred. Please try again.
```

### Edge Cases

- **Empty input**: Treated as default value (if applicable) or re-prompted
- **Whitespace-only input**: Trimmed and validated
- **Very long input**: Truncated at 10,000 characters with warning
- **Special characters**: Accepted in title, description, tags
- **Unicode**: Supported in all text fields

---

## Display Conventions

### Symbols

- `✓` Success indicator
- `✗` Error indicator
- `ℹ` Information indicator
- `===` Section divider

### Formatting

- **Bold**: Not supported in plain text CLI (use UPPERCASE for emphasis)
- **Tables**: Aligned columns with `|` separators
- **Dates**: ISO 8601 format (YYYY-MM-DDTHH:MM:SS) or simplified (YYYY-MM-DD)
- **Status**: "Completed" or "Pending" (not boolean True/False)

### Colors

Phase I does not use ANSI color codes. All output is plain text.

---

## I/O Protocol

### Input

- **Source**: stdin (standard input)
- **Encoding**: UTF-8
- **Line Termination**: `\n` (newline)
- **Blocking**: Yes (waits for user input)

### Output

- **Destination**: stdout (standard output)
- **Encoding**: UTF-8
- **Line Termination**: `\n` (newline)
- **Buffering**: Line-buffered (flush after each prompt)

### Errors

- **Destination**: stderr (standard error) for system errors, stdout for validation errors
- **Encoding**: UTF-8

---

## Testing Contract

### Unit Test Coverage

- Menu display and input parsing
- Input validation for each field type
- Error message formatting
- Table formatting and alignment

### Integration Test Coverage

- Full user journey: launch → add → view → update → delete → exit
- Filter operations with various criteria
- Session summary accuracy
- Error recovery (invalid input → re-prompt → valid input)

### Manual Test Scenarios

- Empty todo list display
- Single todo display
- Many todos (100+) display and performance
- Very long titles/descriptions (boundary conditions)
- Special characters and Unicode in text fields
- Rapid menu navigation (stress test)

---

## Summary

The CLI interface contract defines all user interactions for Phase I. The menu-driven design prioritizes simplicity and discoverability. All operations follow a consistent pattern: prompt → validate → execute → confirm → return to menu. Error handling is graceful with clear messages and re-prompting. The interface is designed to be intuitive for first-time users while remaining efficient for repeated operations.
