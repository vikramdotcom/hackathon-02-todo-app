# Feature Specification: Phase I – In-Memory Python Console Todo App

**Feature Branch**: `001-phase-1-cli-todo`
**Created**: 2026-01-09
**Status**: Draft
**Input**: Evolution of Todo – In-Memory Python Console App with menu-driven CLI and canonical todo data model

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Create and Manage Todos (Priority: P1)

A user opens the CLI todo application and interacts with a menu-driven interface to add, view, and organize their tasks. This is the core user journey.

**Why this priority**: Core value delivery. Without this, no other features are meaningful. P1 establishes the foundation.

**Independent Test**: Can be fully tested by (1) launching the application, (2) adding a todo via menu, (3) viewing the list, and (4) confirming the todo appears with all fields populated. Delivers immediate user value.

**Acceptance Scenarios**:

1. **Given** the user has launched the application, **When** they select "Add Todo" from the main menu, **Then** the system prompts for title (required) and description (optional), assigns a unique auto-incremented ID, records creation timestamp, and stores the todo in memory.
2. **Given** the user has added one or more todos, **When** they select "View Todos", **Then** the system displays all todos with complete details: ID, title, description, completed status, priority, tags, due date, created_at, and updated_at timestamps.
3. **Given** the user is viewing todos, **When** they select "Update Todo" and provide a valid todo ID, **Then** the system allows editing all fields except ID and created_at, preserves the ID and creation timestamp, and updates the updated_at timestamp.
4. **Given** the user has created todos, **When** they select "Delete Todo" and provide a valid ID, **Then** the system removes the todo from memory and displays a confirmation message.
5. **Given** the user is viewing todos, **When** they select "Mark Complete" for a todo, **Then** the completed flag is set to true and updated_at is recorded; when they select "Mark Incomplete", the flag is set to false.

---

### User Story 2 - Filter and Organize Todos (Priority: P2)

A user wants to view their todos filtered by status (completed/incomplete), priority level, or tags to quickly locate relevant tasks among many todos.

**Why this priority**: Increases usability and task discovery. Depends on P1 CRUD operations but adds significant value for users with multiple todos.

**Independent Test**: Can be tested by (1) adding todos with different priorities and tags, (2) selecting filter options (e.g., "Show High Priority"), and (3) confirming only matching todos appear.

**Acceptance Scenarios**:

1. **Given** the user has added todos with varying priorities, **When** they select "Filter by Priority" and choose "High", **Then** only todos marked with priority=high are displayed.
2. **Given** the user has added todos with tags, **When** they select "Filter by Tag" and provide a tag name, **Then** only todos containing that tag are displayed.
3. **Given** the user has completed and incomplete todos, **When** they select "View Completed Todos", **Then** only todos with completed=true are shown; when they select "View Pending Todos", only incomplete todos are shown.

---

### User Story 3 - Recurrence and Due Dates (Priority: P3)

A user wants to set due dates and recurrence patterns for todos to track deadline-sensitive tasks and repeating work (e.g., weekly standup).

**Why this priority**: Adds advanced scheduling capability. Not essential for MVP but valuable for power users managing scheduled tasks. Requires data model support but implementation logic deferred to Phase II.

**Independent Test**: Can be tested by (1) creating a todo with a due date and recurrence pattern, (2) viewing the todo, and (3) confirming dates are stored and displayed.

**Acceptance Scenarios**:

1. **Given** the user is creating a todo, **When** they specify a due date (ISO 8601 format or MM/DD/YYYY), **Then** the system stores the date and displays it in todo listings.
2. **Given** the user is creating a recurring todo, **When** they specify a recurrence pattern (e.g., "daily", "weekly", "monthly"), **Then** the system stores the pattern string.
3. **Given** a todo with a due date, **When** the user views it, **Then** the system displays the due date in a human-readable format.

---

### User Story 4 - Session Summary (Priority: P4)

A user wants to see a session summary before exiting the application, including statistics on operations performed.

**Why this priority**: Nice-to-have feature; does not block MVP delivery. Useful for users auditing their session activity.

**Independent Test**: Can be tested by (1) performing multiple operations (add, update, delete), (2) selecting "Session Summary" or exiting, and (3) confirming the summary displays accurate operation counts.

**Acceptance Scenarios**:

1. **Given** the user has performed multiple operations in the session, **When** they select "Session Summary" or choose "Exit", **Then** the system displays statistics: number of todos added, updated, deleted, and marked complete during this session.

### Edge Cases

- **Empty todo list**: When the user views todos with an empty list, system displays "No todos found" instead of crashing or showing blank output.
- **Invalid todo ID**: When the user provides a non-numeric ID or an ID that doesn't exist, system displays an error message and re-prompts without crashing.
- **Duplicate titles**: Users can create multiple todos with identical titles (titles are not unique; only IDs are unique).
- **Boundary conditions on field lengths**: Title and description accept 1–10,000 characters each. Inputs exceeding limits are rejected with a clear error message.
- **Invalid priority values**: When the user specifies a priority outside (low, medium, high), system displays an error and re-prompts.
- **Malformed dates**: When the user provides an invalid date format, system displays an error and re-prompts, or suggests correct format.
- **Empty title**: When the user attempts to create a todo without a title, system displays an error that title is required and re-prompts.
- **Single-user constraint**: Phase I is single-user, single-session. No concurrency or multi-user scenarios apply.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

**Data Model & Storage**

- **FR-001**: System MUST store todos in memory with the canonical Todo schema: `id` (unique auto-increment integer), `title` (required string, 1–10,000 chars), `description` (optional string, 0–10,000 chars), `completed` (boolean, default false), `priority` (enum: low|medium|high, default medium), `tags` (list of strings, empty list default), `due_date` (ISO 8601 datetime or null), `recurrence` (string pattern or null), `created_at` (datetime on creation, immutable), `updated_at` (datetime on creation, updated on edit).

- **FR-002**: System MUST auto-generate unique integer IDs starting from 1, incrementing by 1 for each new todo, never reusing IDs even if todos are deleted.

- **FR-003**: System MUST initialize with an empty todo list on startup.

**Core Operations**

- **FR-004**: System MUST provide a menu-driven CLI interface with the following options: (1) Add Todo, (2) View All Todos, (3) Update Todo, (4) Delete Todo, (5) Mark Todo Complete, (6) Mark Todo Incomplete, (7) Filter Todos, (8) Session Summary, (9) Exit.

- **FR-005**: System MUST allow users to add a new todo by providing a title (required) and optionally description, priority, tags, due date, and recurrence. All optional fields apply defaults if not provided by the user.

- **FR-006**: System MUST allow users to view all todos, displaying each todo's complete details: ID, title, description, completed status, priority, tags, due date, recurrence, creation timestamp, and last update timestamp.

- **FR-007**: System MUST allow users to update any field of an existing todo by ID, except `id` and `created_at` which are immutable. The `updated_at` timestamp is automatically updated on any edit.

- **FR-008**: System MUST allow users to delete a todo by ID, removing it from memory and confirming deletion with a message.

- **FR-009**: System MUST allow users to mark a todo as completed by setting `completed = true` and recording the `updated_at` timestamp.

- **FR-010**: System MUST allow users to mark a todo as incomplete by setting `completed = false` and recording the `updated_at` timestamp.

**Filtering & Querying**

- **FR-011**: System MUST allow users to filter todos by completion status: "Show Completed", "Show Pending", or "Show All".

- **FR-012**: System MUST allow users to filter todos by priority level: "High", "Medium", "Low", or "All".

- **FR-013**: System MUST allow users to filter by tag: user provides a tag name, and system displays only todos containing that tag.

**User Experience & Input Validation**

- **FR-014**: System MUST display a clear main menu after each operation, prompting the user to select an action.

- **FR-015**: System MUST validate all user input (e.g., todo ID must be numeric and exist in the list, priority must be one of: low, medium, high) and display a clear error message without crashing if input is invalid. After an error, the user is re-prompted.

- **FR-016**: System MUST display todos in a human-readable format (table or list) with clear column headers or labels for each field.

- **FR-017**: System MUST accept date/time input in multiple formats (ISO 8601, MM/DD/YYYY, MM-DD-YYYY, common US/EU formats). Internally, all dates are stored and displayed in ISO 8601 format.

- **FR-018**: System MUST display all timestamps (created_at, updated_at, due_date) in ISO 8601 format by default in the data representation. User-facing display can be human-readable but internal storage/processing is always ISO 8601.

**Session Management**

- **FR-019**: System MUST track operation counts during the current session: number of todos added, updated, deleted, and marked complete/incomplete.

- **FR-020**: System MUST provide a "Session Summary" option accessible from the main menu that displays: total todos currently in memory, count of todos added, updated, deleted, and marked complete during this session.

- **FR-021**: System MUST exit cleanly when the user selects "Exit" from the menu, optionally displaying a final session summary.

**Constraints & Non-Negotiables**

- **FR-022**: System MUST be entirely in-memory; no persistent storage (files, databases, network) is allowed in Phase I.

- **FR-023**: System MUST be single-user and single-session; no multi-user access, authentication, or session recovery is required.

- **FR-024**: System MUST run on Python 3.13+ and use only the Python Standard Library (no third-party dependencies like requests, django, flask, etc.).

- **FR-025**: System MUST be menu-driven, text-based CLI; no graphical UI or web interface in Phase I.

- **FR-026**: All input/output MUST be via stdin/stdout/stderr; no file I/O or network access.

- **FR-027**: System MUST handle input/output errors gracefully (e.g., if stdin is closed unexpectedly, exit cleanly without data corruption).

### Key Entities

- **Todo**: Represents a single task/action item. Immutable fields: `id` (unique identifier), `created_at` (creation timestamp). Editable fields: `title`, `description`, `completed`, `priority`, `tags`, `due_date`, `recurrence`, `updated_at`. Relationships: none in Phase I; in Phase II, todos may be related to users, projects, or categories.

- **Session**: Represents the current CLI session context. Tracks the in-memory todo list, operation counts (added, updated, deleted, completed), and provides access to menu functions. Relationships: contains zero or more todos.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: User can launch the CLI, view the main menu, and complete one full todo operation (add, view, or update) without errors or confusing prompts within 1 minute of launch.

- **SC-002**: System correctly enforces the canonical data model: every todo has all required fields (id, title, completed, priority, created_at, updated_at), IDs are unique and auto-incremented, and timestamps are recorded on creation and update.

- **SC-003**: Each of the five primary operations (add, view, update, delete, mark complete) can be performed independently and produces the expected result without data loss or corruption.

- **SC-004**: Filtering by status (completed/pending), priority (high/medium/low), and tag correctly reduces the displayed todo list to only matching items; filtering with zero results displays a clear "No todos found" message.

- **SC-005**: Invalid user input (non-numeric IDs, out-of-range priorities, malformed dates, missing required fields) is caught and presented with a clear error message; the application does not crash or enter an inconsistent state.

- **SC-006**: Application exits cleanly when the user selects "Exit" and displays a session summary with accurate operation counts (todos added, updated, deleted, marked complete).

- **SC-007**: All timestamps (created_at, updated_at, due_date) are correctly recorded and preserved across all operations; dates are stored in ISO 8601 format internally and never corrupted or lost.

---

## Assumptions

1. **Single-user, single-session architecture**: Phase I does not support multi-user access, concurrent sessions, or session recovery. Each application execution is independent.

2. **In-memory storage only**: No persistent storage is required. Data is lost on exit; this is acceptable and expected for Phase I as a prototype/proof-of-concept.

3. **Standard Python environment**: Assumes Python 3.13+ is installed and available on the user's system via `python` or `python3` command.

4. **Terminal-based I/O**: The CLI reads from stdin and writes to stdout/stderr; assumes a standard terminal environment (no special terminal handling required beyond standard ANSI).

5. **Date format flexibility**: Users can input dates in multiple common formats (ISO 8601, MM/DD/YYYY, MM-DD-YYYY, other common US/EU formats). System converts to ISO 8601 for internal storage.

6. **Reasonable defaults for optional fields**: If a user does not specify optional fields (description, priority, tags, due_date, recurrence), the system applies reasonable defaults: `description=""`, `priority="medium"`, `tags=[]`, `due_date=null`, `recurrence=null`.

7. **No external APIs or services**: Phase I is entirely self-contained. No network calls, external authentication, or third-party service dependencies.

8. **Error handling preference**: On invalid input, the system re-prompts the user rather than exiting or requiring a restart. This prioritizes user experience and exploration.

9. **Backward compatibility deferred**: Phase I is not required to maintain backward compatibility with future phases' APIs; the data model and core operations will remain consistent, but implementation details may change.

---

## Non-Goals

- **Multi-user support**: User authentication, permission management, and multi-user data isolation are not in scope for Phase I.
- **Persistent storage**: Database, file-based persistence, or any form of data survival beyond the session are not in scope.
- **Web or graphical user interface**: All interaction is via CLI; web UI and GUI are Phase II goals.
- **AI-powered conversational interface**: Natural language processing and AI agents are Phase III goals.
- **Automatic recurrence processing**: Recurrence patterns are stored but not automatically actioned (e.g., no automatic creation of next occurrence). Processing is deferred to Phase II.
- **Integrations with external services**: Email notifications, calendar sync, or third-party service integrations are not in scope.
- **Performance optimization**: Phase I prioritizes correctness and completeness over performance; performance optimization is a later-phase concern.
- **Advanced scheduling features**: Reminders, notifications, or time-zone support are not in scope for Phase I.

---

## Acceptance Testing Strategy

### Unit Testing Candidates (for `/sp.plan` and implementation)

- ID auto-increment logic: each new todo gets next available ID, IDs never reused
- Input validation: title required, ID format, priority enum constraints, date format acceptance
- Todo CRUD operations: create, read (view all), update (each field), delete, toggle complete/incomplete
- Filter logic: by status, priority, tag; empty result handling
- Session tracking: operation count accuracy
- Timestamp handling: creation, updates, ISO 8601 format preservation
- Field length limits: title and description boundary conditions (0, 1, 10000, 10001 chars)

### Integration Testing Candidates

- End-to-end user journey: launch → add todo → view todos → update todo → delete todo → exit
- Menu navigation: all options accessible, re-prompting on error, menu displays after each operation
- Data consistency: operations in sequence don't corrupt state; ID uniqueness maintained
- Filter combinations: filtering multiple times in sequence, filtering empty list, clearing filters

### Manual Testing

- **Usability**: Is the menu clear and self-explanatory? Are error messages helpful and actionable?
- **Edge cases**: empty todo list, single todo, many todos (100+), very long titles/descriptions
- **Input variety**: different date formats, various priority levels, many tags per todo
- **Timestamp accuracy**: confirm created_at is immutable, updated_at changes on each edit
- **Session summary**: verify operation counts are accurate after various sequences of operations

---

## Future Phase Compatibility Notes

- **Phase II (Full-stack Web Application)**: This spec defines the data model and operations semantics. Phase II will expose the same operations via HTTP REST API and add file-based or database persistence. The in-memory todo list from Phase I can be refactored into a shared library/module.

- **Phase III (AI-powered Conversational Todo Management)**: The todo operations are abstracted and will be accessible via natural language commands. An AI agent will translate user intent into the core operations defined here.

- **Phase IV (Local Kubernetes Deployment)**: The data model and operation semantics remain unchanged. Deployment changes to containerized, orchestrated setup with service boundaries and inter-service communication.

- **Phase V (Cloud-native Distributed Deployment)**: Data model and core operations unchanged. Deployment spans multiple regions, introduces eventual consistency, and serverless compute patterns.

---

## Technology Constraints

- **Programming Language**: Python 3.13+ only. No other languages in Phase I.
- **Dependencies**: Standard Library only. Zero third-party packages (no requests, django, flask, pandas, etc.).
- **I/O Protocol**: stdin/stdout/stderr. No file operations, no network sockets, no database connections.
- **Concurrency**: Single-threaded execution. No async, threading, multiprocessing, or concurrent operations.
- **Data Structures**: In-memory lists, dictionaries, and standard Python types only.
