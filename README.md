# Phase I CLI Todo App

A menu-driven Python console application for managing todos in memory.

## Overview

Phase I delivers a CLI application implementing the canonical Todo data model with full CRUD operations, filtering by status/priority/tags, and session tracking. The application follows a three-layer architecture: Domain (Todo model), Service (TodoManager), and Interface (CLI menu).

## Prerequisites

- Python 3.13 or later
- Terminal/Command Prompt access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hackathon-02-todo-app
git checkout 001-phase-1-cli-todo
```

2. Verify Python version:
```bash
python --version  # Should be 3.13.x or later
```

## Running the Application

Launch the CLI:
```bash
python src/main.py
```

## Features

### User Story 1 (P1) - Core CRUD Operations
- Add todos with title, description, priority, tags, due date, and recurrence
- View all todos in a formatted table
- Update existing todos (all fields except ID and created_at)
- Delete todos with confirmation
- Mark todos as complete/incomplete
- Session tracking for all operations

### User Story 2 (P2) - Filtering
- Filter by status (completed/pending)
- Filter by priority (high/medium/low)
- Filter by tag

### User Story 3 (P3) - Date Support
- Set due dates (ISO 8601, MM/DD/YYYY, MM-DD-YYYY formats)
- Set recurrence patterns (storage only, no automatic processing)

### User Story 4 (P4) - Session Summary
- View session statistics (todos added, updated, deleted, completed)
- Display summary on exit

## Project Structure

```
src/
├── models/
│   ├── todo.py          # Todo domain model
│   └── session.py       # Session context
├── services/
│   └── todo_service.py  # TodoManager service
├── cli/
│   ├── menu.py          # CLI menu interface
│   └── validators.py    # Input validation utilities
└── main.py              # Application entry point

tests/
├── unit/                # Unit tests
└── integration/         # Integration tests
```

## Usage

### Quick Tutorial

1. **Add a todo**: Select option 1, enter title and optional fields
2. **View todos**: Select option 2 to see all todos in a table
3. **Update a todo**: Select option 3, enter ID, and update fields
4. **Delete a todo**: Select option 4, enter ID, and confirm
5. **Mark complete**: Select option 5, enter ID
6. **Filter todos**: Select option 7 for filtering options
7. **Session summary**: Select option 8 to view statistics
8. **Exit**: Select option 9 to exit with summary

## Limitations (Phase I)

- **In-memory storage**: All data is lost when you exit
- **Single-user**: No authentication or multi-user support
- **CLI only**: No web interface or API

## Future Phases

- **Phase II**: Web application with REST API and database persistence
- **Phase III**: AI-powered conversational interface
- **Phase IV**: Local Kubernetes deployment
- **Phase V**: Cloud-native distributed deployment

## Documentation

- Feature Specification: `specs/001-phase-1-cli-todo/spec.md`
- Implementation Plan: `specs/001-phase-1-cli-todo/plan.md`
- Data Model: `specs/001-phase-1-cli-todo/data-model.md`
- CLI Interface Contract: `specs/001-phase-1-cli-todo/contracts/cli-interface.md`
- Quickstart Guide: `specs/001-phase-1-cli-todo/quickstart.md`

## License

[Add license information]
