# Research & Technical Decisions: Phase I CLI Todo App

**Feature**: Phase I – In-Memory Python Console Todo App
**Branch**: `001-phase-1-cli-todo`
**Date**: 2026-01-09

## Overview

This document captures the technical research and decision rationale for Phase I implementation. Since the feature specification (spec.md) provides explicit technical constraints, no open research questions exist. This document serves as a record of the decisions made and alternatives considered.

## Technical Decisions

### 1. Programming Language: Python 3.13+

**Decision**: Use Python 3.13 or later as the implementation language.

**Rationale**:
- Explicitly required by spec.md (FR-024, Technology Constraints)
- Python 3.13 provides modern language features (improved error messages, better performance)
- Cross-platform compatibility (Windows, macOS, Linux)
- Rich standard library eliminates need for third-party dependencies
- Excellent support for dataclasses, type hints, and datetime handling

**Alternatives Considered**:
- **Python 3.11/3.12**: Would work but 3.13 is specified as minimum version
- **Other languages**: Not considered; Python is a hard requirement per spec

**Trade-offs**:
- ✅ Pros: Rapid development, excellent standard library, readable code
- ⚠️ Cons: Slower than compiled languages (not relevant for Phase I scale)

---

### 2. Dependency Management: Standard Library Only

**Decision**: Use only Python Standard Library; zero third-party packages.

**Rationale**:
- Explicitly required by spec.md (FR-024)
- Eliminates dependency management complexity
- Ensures maximum portability and minimal setup friction
- Standard library provides all necessary functionality:
  - `dataclasses` for Todo model
  - `datetime` for timestamp handling
  - `unittest` for testing
  - `sys`, `os` for I/O and environment

**Alternatives Considered**:
- **pytest**: Better testing framework but violates zero-dependency constraint
- **pydantic**: Excellent validation but third-party dependency
- **click/typer**: CLI frameworks but unnecessary for simple menu-driven interface

**Trade-offs**:
- ✅ Pros: Zero setup, no version conflicts, maximum portability
- ⚠️ Cons: More manual validation code, less sophisticated testing features

---

### 3. Data Storage: In-Memory Python Data Structures

**Decision**: Store todos in a Python list, managed by TodoManager service.

**Rationale**:
- Explicitly required by spec.md (FR-022): "entirely in-memory"
- Simple, fast, and sufficient for Phase I prototype
- No file I/O or database setup required
- Data structures:
  - `List[Todo]` for todo storage
  - `Dict[str, int]` for session operation tracking
  - Auto-increment ID via `max(todo.id for todo in todos) + 1`

**Alternatives Considered**:
- **File-based persistence**: Violates Phase I constraints (deferred to Phase II)
- **SQLite in-memory**: Overkill for simple list operations; adds complexity
- **Dictionary by ID**: Considered but list is simpler for filtering/iteration

**Trade-offs**:
- ✅ Pros: Simplest possible implementation, no I/O errors, fast operations
- ⚠️ Cons: Data lost on exit (acceptable for Phase I prototype)

---

### 4. Testing Framework: unittest (Standard Library)

**Decision**: Use `unittest` module from Python standard library.

**Rationale**:
- Part of standard library; no third-party dependencies
- Sufficient for unit and integration testing needs
- Well-documented and widely understood
- Supports test discovery, fixtures, assertions, and mocking

**Alternatives Considered**:
- **pytest**: Superior features (fixtures, parametrization) but third-party dependency
- **doctest**: Too limited for comprehensive testing
- **Manual testing only**: Insufficient for validating acceptance criteria

**Trade-offs**:
- ✅ Pros: No dependencies, adequate for Phase I scope
- ⚠️ Cons: More verbose than pytest, less powerful fixtures

---

### 5. Architecture Pattern: Three-Layer (Domain, Service, Interface)

**Decision**: Organize code into three layers:
- **Domain Layer** (`src/models/todo.py`): Todo dataclass with validation
- **Service Layer** (`src/services/todo_service.py`): TodoManager with business logic
- **Interface Layer** (`src/cli/menu.py`): CLI menu and user interaction

**Rationale**:
- Separation of concerns: domain logic, business operations, user interface
- Service layer is reusable in Phase II (REST API can call same TodoManager methods)
- Testable: each layer can be unit tested independently
- Aligns with spec.md's "Evolution Hooks" requirement

**Alternatives Considered**:
- **Single-file monolith**: Simpler but not forward-compatible with Phase II
- **MVC pattern**: Overkill for CLI application; no "view" rendering needed
- **Hexagonal/ports-adapters**: Too complex for Phase I scope

**Trade-offs**:
- ✅ Pros: Clean separation, reusable service layer, testable
- ⚠️ Cons: Slightly more files/boilerplate than monolith

---

### 6. Date/Time Handling: ISO 8601 with datetime Module

**Decision**: Use Python's `datetime` module; store all timestamps as `datetime` objects; serialize to ISO 8601 strings for display.

**Rationale**:
- Spec.md requires ISO 8601 format (FR-017, FR-018)
- `datetime.datetime.now()` for `created_at` and `updated_at`
- `datetime.fromisoformat()` for parsing user input
- `datetime.isoformat()` for display

**Alternatives Considered**:
- **Store as strings**: Loses type safety and comparison capabilities
- **Unix timestamps**: Not human-readable; violates ISO 8601 requirement
- **Third-party libraries (arrow, pendulum)**: Violates zero-dependency constraint

**Trade-offs**:
- ✅ Pros: Type-safe, standard library, ISO 8601 compliant
- ⚠️ Cons: Manual parsing for multiple input formats (MM/DD/YYYY, etc.)

---

### 7. Input Validation Strategy: Validate Early, Re-prompt on Error

**Decision**: Validate all user input at the CLI layer; display clear error messages; re-prompt without crashing.

**Rationale**:
- Spec.md requires graceful error handling (FR-015)
- User experience priority: exploration-friendly, forgiving interface
- Validation rules:
  - Todo ID: must be numeric and exist in list
  - Priority: must be one of {low, medium, high}
  - Title: required, 1-10,000 characters
  - Description: optional, 0-10,000 characters
  - Dates: flexible input formats, convert to ISO 8601

**Alternatives Considered**:
- **Crash on invalid input**: Poor user experience
- **Silent failures**: Confusing and violates spec requirements
- **Validation in service layer**: Considered but CLI layer is better for user-facing errors

**Trade-offs**:
- ✅ Pros: User-friendly, clear error messages, robust
- ⚠️ Cons: More validation code in CLI layer

---

### 8. CLI Menu Design: Numbered Menu with Loop

**Decision**: Display numbered menu options; read user choice; execute action; loop back to menu.

**Rationale**:
- Spec.md requires menu-driven interface (FR-004)
- Simple, intuitive, no learning curve
- Menu options map directly to functional requirements:
  1. Add Todo (FR-005)
  2. View All Todos (FR-006)
  3. Update Todo (FR-007)
  4. Delete Todo (FR-008)
  5. Mark Complete (FR-009)
  6. Mark Incomplete (FR-010)
  7. Filter Todos (FR-011, FR-012, FR-013)
  8. Session Summary (FR-020)
  9. Exit (FR-021)

**Alternatives Considered**:
- **Command-line arguments**: Less interactive, harder to explore
- **Natural language**: Deferred to Phase III (AI-powered interface)
- **TUI framework (curses)**: Overkill for simple menu

**Trade-offs**:
- ✅ Pros: Simple, intuitive, easy to implement
- ⚠️ Cons: Less efficient for power users (no shortcuts)

---

## Research Findings Summary

**No open research questions.** All technical decisions are explicitly specified in spec.md or follow directly from the constraints. The architecture is straightforward: three-layer pattern with in-memory storage, standard library only, and menu-driven CLI.

**Key Risks Identified**:
1. **Date parsing complexity**: Supporting multiple input formats (ISO 8601, MM/DD/YYYY, etc.) requires careful parsing logic. Mitigation: Use `datetime.fromisoformat()` for ISO 8601; add manual parsing for common formats.
2. **ID collision after deletion**: If todos are deleted, ID generation must not reuse IDs. Mitigation: Track max ID separately or always compute `max(todo.id) + 1`.
3. **Large todo lists**: In-memory storage limits practical use to ~1000 todos. Mitigation: Acceptable for Phase I prototype; Phase II adds persistence.

**Next Steps**: Proceed to Phase 1 (data-model.md, contracts/, quickstart.md).
