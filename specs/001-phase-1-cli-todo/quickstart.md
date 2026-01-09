# Quickstart Guide: Phase I CLI Todo App

**Feature**: Phase I – In-Memory Python Console Todo App
**Branch**: `001-phase-1-cli-todo`
**Date**: 2026-01-09

## Overview

This quickstart guide provides step-by-step instructions for setting up, running, and using the Phase I CLI Todo Application. The application is a menu-driven Python console tool for managing todos in memory.

## Prerequisites

- **Python 3.13 or later** installed on your system
- **Terminal/Command Prompt** access
- **Git** (optional, for cloning the repository)

### Verify Python Installation

```bash
python --version
# or
python3 --version
```

Expected output: `Python 3.13.x` or later

---

## Installation

### Option 1: Clone from Repository

```bash
git clone <repository-url>
cd hackathon-02-todo-app
git checkout 001-phase-1-cli-todo
```

### Option 2: Download Source

Download the source code and extract to a directory of your choice.

---

## Project Structure

```
hackathon-02-todo-app/
├── src/
│   ├── models/
│   │   └── todo.py          # Todo domain model
│   ├── services/
│   │   └── todo_service.py  # TodoManager service
│   ├── cli/
│   │   └── menu.py          # CLI menu interface
│   └── main.py              # Application entry point
├── tests/
│   ├── unit/
│   │   ├── test_todo_model.py
│   │   ├── test_todo_service.py
│   │   └── test_cli_menu.py
│   └── integration/
│       └── test_end_to_end.py
├── specs/
│   └── 001-phase-1-cli-todo/
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md (this file)
│       └── contracts/
│           └── cli-interface.md
├── README.md
└── requirements.txt (empty - no dependencies)
```

---

## Running the Application

### Launch the CLI

```bash
python src/main.py
# or
python3 src/main.py
```

### Expected Output

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

---

## Quick Tutorial

### 1. Add Your First Todo

1. Select option `1` (Add Todo)
2. Enter a title: `Buy groceries`
3. Enter description (optional): `Get milk, eggs, bread`
4. Enter priority: `high`
5. Enter tags: `shopping, errands`
6. Enter due date: `2026-01-10`
7. Enter recurrence: (press Enter to skip)

**Result**:
```
✓ Todo created successfully!
  ID: 1
  Title: Buy groceries
  Created: 2026-01-09T14:30:00
```

### 2. View All Todos

1. Select option `2` (View All Todos)

**Result**:
```
=== All Todos (1 total) ===

ID | Title              | Status    | Priority | Due Date   | Tags
---|--------------------|-----------|-----------|-----------|---------
1  | Buy groceries      | Pending   | high     | 2026-01-10 | shopping, errands

Press Enter to continue...
```

### 3. Mark Todo Complete

1. Select option `5` (Mark Todo Complete)
2. Enter todo ID: `1`

**Result**:
```
✓ Todo marked as complete!
  ID: 1
  Title: Buy groceries
```

### 4. View Session Summary

1. Select option `8` (Session Summary)

**Result**:
```
=== Session Summary ===

Total Todos: 1
  - Completed: 1
  - Pending: 0

Operations This Session:
  - Todos Added: 1
  - Todos Updated: 0
  - Todos Deleted: 0
  - Todos Marked Complete: 1

Press Enter to continue...
```

### 5. Exit Application

1. Select option `9` (Exit)

**Result**:
```
=== Session Summary ===

Total Todos: 1
  - Completed: 1
  - Pending: 0

Operations This Session:
  - Todos Added: 1
  - Todos Updated: 0
  - Todos Deleted: 0
  - Todos Marked Complete: 1

Thank you for using Todo Application!
Goodbye!
```

---

## Common Operations

### Adding Multiple Todos

Repeat the "Add Todo" operation (option 1) for each task. Each todo receives a unique auto-incremented ID.

### Updating a Todo

1. Select option `3` (Update Todo)
2. Enter the todo ID
3. For each field, enter a new value or press Enter to keep the current value

### Deleting a Todo

1. Select option `4` (Delete Todo)
2. Enter the todo ID
3. Confirm deletion by entering `y`

**Note**: Deleted todo IDs are never reused.

### Filtering Todos

1. Select option `7` (Filter Todos)
2. Choose filter type:
   - **By Status**: Show completed, pending, or all todos
   - **By Priority**: Show high, medium, low, or all priorities
   - **By Tag**: Show todos containing a specific tag
3. View filtered results
4. Select option `4` to return to main menu

---

## Running Tests

### Run All Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

### Run Unit Tests Only

```bash
python -m unittest discover -s tests/unit -p "test_*.py"
```

### Run Integration Tests Only

```bash
python -m unittest discover -s tests/integration -p "test_*.py"
```

### Run Specific Test File

```bash
python -m unittest tests.unit.test_todo_model
```

### Expected Test Output

```
...........
----------------------------------------------------------------------
Ran 11 tests in 0.123s

OK
```

---

## Troubleshooting

### Issue: "Python not found"

**Solution**: Ensure Python 3.13+ is installed and added to your system PATH.

```bash
# Windows
where python

# macOS/Linux
which python3
```

### Issue: "ModuleNotFoundError"

**Solution**: Ensure you're running the command from the repository root directory.

```bash
cd hackathon-02-todo-app
python src/main.py
```

### Issue: "Invalid choice" error

**Solution**: Enter a number between 1 and 9. Non-numeric input is rejected.

### Issue: "Title is required" error

**Solution**: Title field cannot be empty. Enter at least one character.

### Issue: "Todo with ID X not found"

**Solution**: Verify the todo ID exists by viewing all todos (option 2) first.

---

## Tips and Best Practices

### Efficient Workflow

1. **Add todos in batch**: Add all your tasks at the start of the session
2. **Use filters**: Quickly find todos by status, priority, or tag
3. **Check session summary**: Review your progress before exiting

### Input Shortcuts

- **Press Enter**: Skip optional fields (description, tags, due date, recurrence)
- **Default priority**: If you press Enter for priority, it defaults to "medium"
- **Multiple tags**: Separate tags with commas: `work, urgent, project-x`

### Date Formats

The application accepts multiple date formats:
- ISO 8601: `2026-01-10`
- US format: `01/10/2026`
- Alternative: `01-10-2026`

All dates are stored and displayed in ISO 8601 format internally.

---

## Limitations (Phase I)

### In-Memory Storage

- **Data is not saved**: All todos are lost when you exit the application
- **Single session**: No way to recover previous sessions
- **No persistence**: Files, databases, and network storage are not supported

### Single-User

- **No authentication**: Anyone with access to the terminal can use the app
- **No multi-user**: Only one person can use the app at a time
- **No concurrency**: No support for multiple simultaneous sessions

### CLI Only

- **No GUI**: Text-based interface only
- **No web interface**: Web UI is planned for Phase II
- **No API**: REST API is planned for Phase II

---

## Next Steps

### Phase II: Full-Stack Web Application

Phase II will add:
- Web-based user interface
- REST API for programmatic access
- Database persistence (SQLite or PostgreSQL)
- Multi-user support with authentication

### Phase III: AI-Powered Conversational Interface

Phase III will add:
- Natural language processing
- AI agent for conversational todo management
- Voice input support

### Phase IV & V: Kubernetes and Cloud Deployment

Later phases will add:
- Containerization and orchestration
- Multi-region deployment
- Scalability and high availability

---

## Getting Help

### Documentation

- **Feature Specification**: `specs/001-phase-1-cli-todo/spec.md`
- **Implementation Plan**: `specs/001-phase-1-cli-todo/plan.md`
- **Data Model**: `specs/001-phase-1-cli-todo/data-model.md`
- **CLI Interface Contract**: `specs/001-phase-1-cli-todo/contracts/cli-interface.md`

### Reporting Issues

If you encounter bugs or have feature requests, please report them via the project's issue tracker.

---

## Summary

The Phase I CLI Todo Application is a simple, menu-driven tool for managing tasks in memory. It provides full CRUD operations, filtering, and session tracking. While data is not persisted, the application serves as a prototype for the canonical Todo data model that will be used across all five phases of the project.

**Key Commands**:
- Launch: `python src/main.py`
- Run tests: `python -m unittest discover -s tests`
- Exit: Select option `9` from the main menu

Enjoy managing your todos!
