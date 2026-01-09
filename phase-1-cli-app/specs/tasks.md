# Tasks: Phase I – In-Memory Python Console Todo App

**Input**: Design documents from `/specs/001-phase-1-cli-todo/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the feature specification. This task list focuses on implementation only. Unit and integration tests can be added later if needed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below follow the structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure: src/, src/models/, src/services/, src/cli/, tests/, tests/unit/, tests/integration/
- [x] T002 Create empty __init__.py files in src/, src/models/, src/services/, src/cli/ for Python package structure
- [x] T003 [P] Create requirements.txt (empty file - no third-party dependencies)
- [x] T004 [P] Create .gitignore with Python standard ignores (__pycache__/, *.pyc, *.pyo, .pytest_cache/, etc.)
- [x] T005 [P] Create README.md with project overview and setup instructions per quickstart.md

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Implement Todo dataclass in src/models/todo.py with all 10 fields (id, title, description, completed, priority, tags, due_date, recurrence, created_at, updated_at)
- [x] T007 Add validation methods to Todo class: _validate_title(), _validate_priority(), _validate_description() per data-model.md
- [x] T008 Add __post_init__() method to Todo class to trigger validation on instantiation
- [x] T009 [P] Implement Session dataclass in src/models/session.py with fields: todos (List[Todo]), next_id (int), operations (Dict[str, int])
- [x] T010 [P] Add Session initialization method to create empty session with todos=[], next_id=1, operations={"added": 0, "updated": 0, "deleted": 0, "completed": 0}
- [x] T011 [P] Create input validation utilities in src/cli/validators.py for ID validation, priority validation, date parsing

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Manage Todos (Priority: P1) 🎯 MVP

**Goal**: Enable users to add, view, update, delete, and mark todos complete/incomplete via menu-driven CLI

**Independent Test**: Launch application → Add todo → View todos → Update todo → Delete todo → Mark complete → Exit. Verify all operations work correctly and data persists within session.

### Implementation for User Story 1

- [x] T012 [US1] Create TodoManager class in src/services/todo_service.py with __init__(self, session: Session) method
- [x] T013 [US1] Implement TodoManager.add_todo(title, description, priority, tags, due_date, recurrence) method that generates ID, creates Todo, adds to session, increments operations["added"]
- [x] T014 [US1] Implement TodoManager.get_all_todos() method that returns session.todos list
- [x] T015 [US1] Implement TodoManager.get_todo_by_id(todo_id) method that finds and returns todo or raises ValueError if not found
- [x] T016 [US1] Implement TodoManager.update_todo(todo_id, **fields) method that updates mutable fields, preserves id/created_at, updates updated_at, increments operations["updated"]
- [x] T017 [US1] Implement TodoManager.delete_todo(todo_id) method that removes todo from session, increments operations["deleted"]
- [x] T018 [US1] Implement TodoManager.mark_complete(todo_id) and mark_incomplete(todo_id) methods that update completed flag, updated_at, increment operations["completed"]
- [x] T019 [US1] Create MenuDisplay class in src/cli/menu.py with display_main_menu() method that prints menu options 1-9 per cli-interface.md
- [x] T020 [US1] Implement MenuDisplay.display_todos(todos) method that formats and prints todo table with columns: ID, Title, Status, Priority, Due Date, Tags
- [x] T021 [US1] Implement MenuDisplay.display_success(message) and display_error(message) methods with ✓ and ✗ symbols
- [x] T022 [US1] Create MenuHandler class in src/cli/menu.py with __init__(self, todo_manager: TodoManager) method
- [x] T023 [US1] Implement MenuHandler.handle_add_todo() method that prompts for title, description, priority, tags, due_date, recurrence, validates input, calls todo_manager.add_todo()
- [x] T024 [US1] Implement MenuHandler.handle_view_todos() method that calls todo_manager.get_all_todos() and displays via MenuDisplay
- [x] T025 [US1] Implement MenuHandler.handle_update_todo() method that prompts for ID, displays current values, prompts for new values, validates, calls todo_manager.update_todo()
- [x] T026 [US1] Implement MenuHandler.handle_delete_todo() method that prompts for ID, confirms deletion, calls todo_manager.delete_todo()
- [x] T027 [US1] Implement MenuHandler.handle_mark_complete() and handle_mark_incomplete() methods that prompt for ID, call todo_manager methods
- [x] T028 [US1] Implement MenuHandler.run() method that displays menu, reads choice, dispatches to appropriate handler, loops until exit
- [x] T029 [US1] Create main.py entry point that initializes Session, TodoManager, MenuHandler, and calls handler.run()
- [x] T030 [US1] Add error handling in MenuHandler methods to catch ValueError, display error message, re-prompt user per cli-interface.md

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. User can perform all CRUD operations.

---

## Phase 4: User Story 2 - Filter and Organize Todos (Priority: P2)

**Goal**: Enable users to filter todos by status (completed/pending), priority (high/medium/low), and tags

**Independent Test**: Add todos with different priorities and tags → Select "Filter Todos" → Filter by priority "high" → Verify only high-priority todos displayed → Filter by tag → Verify only matching todos displayed.

### Implementation for User Story 2

- [x] T031 [US2] Implement TodoManager.filter_by_status(status: str) method that returns todos where completed matches status ("completed", "pending", or "all")
- [x] T032 [P] [US2] Implement TodoManager.filter_by_priority(priority: str) method that returns todos where priority matches ("high", "medium", "low", or "all")
- [x] T033 [P] [US2] Implement TodoManager.filter_by_tag(tag: str) method that returns todos where tag is in tags list
- [x] T034 [US2] Create MenuDisplay.display_filter_menu() method that prints filter submenu options 1-4 per cli-interface.md
- [x] T035 [US2] Implement MenuHandler.handle_filter_todos() method that displays filter menu, reads choice, dispatches to filter handlers
- [x] T036 [US2] Implement MenuHandler.handle_filter_by_status() method that prompts for status choice (1=Completed, 2=Pending, 3=All), calls todo_manager.filter_by_status(), displays results
- [x] T037 [US2] Implement MenuHandler.handle_filter_by_priority() method that prompts for priority choice (1=High, 2=Medium, 3=Low, 4=All), calls todo_manager.filter_by_priority(), displays results
- [x] T038 [US2] Implement MenuHandler.handle_filter_by_tag() method that prompts for tag name, calls todo_manager.filter_by_tag(), displays results
- [x] T039 [US2] Update MenuHandler.run() to handle menu option 7 (Filter Todos) by calling handle_filter_todos()
- [x] T040 [US2] Add empty result handling in filter handlers to display "No todos match the selected filter" message per cli-interface.md

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. User can filter todos by multiple criteria.

---

## Phase 5: User Story 3 - Recurrence and Due Dates (Priority: P3)

**Goal**: Enable users to set due dates and recurrence patterns for todos (storage only, no automatic processing)

**Independent Test**: Add todo with due date "2026-01-15" and recurrence "weekly" → View todo → Verify due date and recurrence are displayed correctly.

### Implementation for User Story 3

- [x] T041 [P] [US3] Implement parse_date(date_string: str) function in src/cli/validators.py that accepts ISO 8601, MM/DD/YYYY, MM-DD-YYYY formats and returns datetime object or None
- [x] T042 [P] [US3] Implement format_date(date: Optional[datetime]) function in src/cli/validators.py that converts datetime to ISO 8601 string or "None" for display
- [x] T043 [US3] Update MenuHandler.handle_add_todo() to parse due_date input using parse_date() before passing to todo_manager.add_todo()
- [x] T044 [US3] Update MenuHandler.handle_update_todo() to parse due_date input using parse_date() when updating due_date field
- [x] T045 [US3] Update MenuDisplay.display_todos() to include due_date and recurrence columns in table output using format_date()
- [x] T046 [US3] Add date format validation in MenuHandler.handle_add_todo() and handle_update_todo() to display error message if date parsing fails per cli-interface.md

**Checkpoint**: All user stories 1, 2, and 3 should now be independently functional. User can set and view due dates and recurrence patterns.

---

## Phase 6: User Story 4 - Session Summary (Priority: P4)

**Goal**: Enable users to view session statistics (todos added, updated, deleted, completed) and display summary on exit

**Independent Test**: Perform multiple operations (add 3 todos, update 1, delete 1, mark 1 complete) → Select "Session Summary" → Verify counts are accurate → Exit → Verify summary displayed again.

### Implementation for User Story 4

- [x] T047 [US4] Implement TodoManager.get_session_summary() method that returns dict with total_todos, completed_count, pending_count, and operations counts
- [x] T048 [US4] Create MenuDisplay.display_session_summary(summary: dict) method that formats and prints session statistics per cli-interface.md format
- [x] T049 [US4] Implement MenuHandler.handle_session_summary() method that calls todo_manager.get_session_summary() and displays via MenuDisplay
- [x] T050 [US4] Update MenuHandler.run() to handle menu option 8 (Session Summary) by calling handle_session_summary()
- [x] T051 [US4] Implement MenuHandler.handle_exit() method that displays session summary, prints "Thank you for using Todo Application! Goodbye!", and exits
- [x] T052 [US4] Update MenuHandler.run() to handle menu option 9 (Exit) by calling handle_exit() and breaking the menu loop

**Checkpoint**: All user stories should now be independently functional. Application provides complete session tracking and graceful exit.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [x] T053 [P] Add comprehensive input validation error messages for all MenuHandler methods per cli-interface.md error handling patterns
- [x] T054 [P] Add edge case handling: empty todo list display, invalid ID handling, whitespace-only input trimming
- [x] T055 [P] Add field length validation in MenuHandler.handle_add_todo() and handle_update_todo() for title (1-10,000 chars) and description (0-10,000 chars)
- [x] T056 [P] Add duplicate tag removal in MenuHandler.handle_add_todo() and handle_update_todo() when parsing comma-separated tags
- [x] T057 [P] Add confirmation prompt in MenuHandler.handle_delete_todo() per cli-interface.md ("Are you sure? Confirm (y/n)")
- [x] T058 [P] Add "Press Enter to continue..." prompts after display operations (view todos, filter results, session summary) per cli-interface.md
- [x] T059 [P] Verify all menu operations return to main menu after completion per cli-interface.md behavior
- [x] T060 [P] Add graceful handling for stdin/stdout errors (EOFError, KeyboardInterrupt) to exit cleanly per FR-027
- [x] T061 Update README.md with final usage instructions, examples, and quickstart guide content
- [x] T062 Run manual validation against all acceptance criteria (SC-001 through SC-007) from spec.md
- [x] T063 Verify all functional requirements (FR-001 through FR-027) are implemented per spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (Phase 3): Can start after Foundational - No dependencies on other stories
  - User Story 2 (Phase 4): Can start after Foundational - Depends on US1 TodoManager and MenuHandler classes
  - User Story 3 (Phase 5): Can start after Foundational - Depends on US1 MenuHandler methods for integration
  - User Story 4 (Phase 6): Can start after Foundational - Depends on US1 TodoManager and MenuHandler classes
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories. Establishes TodoManager and MenuHandler classes used by other stories.
- **User Story 2 (P2)**: Can start after US1 core classes exist - Adds filtering methods to TodoManager and filter handlers to MenuHandler
- **User Story 3 (P3)**: Can start after US1 core classes exist - Enhances existing add/update/view operations with date handling
- **User Story 4 (P4)**: Can start after US1 core classes exist - Adds session summary methods to TodoManager and MenuHandler

### Within Each User Story

- **US1**: Todo model → Session model → TodoManager service → MenuDisplay → MenuHandler → main.py entry point
- **US2**: Filter methods in TodoManager → Filter menu display → Filter handlers in MenuHandler
- **US3**: Date parsing utilities → Integration into add/update/view handlers
- **US4**: Session summary method → Summary display → Exit handler

### Parallel Opportunities

- **Phase 1 (Setup)**: T003, T004, T005 can run in parallel (different files)
- **Phase 2 (Foundational)**: T009, T010, T011 can run in parallel after T006-T008 complete (different files)
- **Phase 3 (US1)**: T019, T020, T021 (MenuDisplay methods) can run in parallel with T012-T018 (TodoManager methods)
- **Phase 4 (US2)**: T031, T032, T033 (filter methods) can run in parallel (different methods in same file)
- **Phase 5 (US3)**: T041, T042 (date utilities) can run in parallel (different functions in same file)
- **Phase 7 (Polish)**: T053, T054, T055, T056, T057, T058, T059, T060 can run in parallel (different concerns)

---

## Parallel Example: User Story 1

```bash
# Launch TodoManager methods together (T012-T018):
Task: "Create TodoManager class in src/services/todo_service.py"
Task: "Implement TodoManager.add_todo() method"
Task: "Implement TodoManager.get_all_todos() method"
Task: "Implement TodoManager.get_todo_by_id() method"
Task: "Implement TodoManager.update_todo() method"
Task: "Implement TodoManager.delete_todo() method"
Task: "Implement TodoManager.mark_complete() and mark_incomplete() methods"

# Launch MenuDisplay methods together (T019-T021):
Task: "Create MenuDisplay class with display_main_menu() method"
Task: "Implement MenuDisplay.display_todos() method"
Task: "Implement MenuDisplay.display_success() and display_error() methods"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T011) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T012-T030)
4. **STOP and VALIDATE**: Test User Story 1 independently against acceptance scenarios
5. Deploy/demo if ready - this is a functional todo app!

### Incremental Delivery

1. Complete Setup + Foundational (T001-T011) → Foundation ready
2. Add User Story 1 (T012-T030) → Test independently → **MVP DELIVERED** ✅
3. Add User Story 2 (T031-T040) → Test independently → Filtering capability added
4. Add User Story 3 (T041-T046) → Test independently → Date/recurrence support added
5. Add User Story 4 (T047-T052) → Test independently → Session tracking complete
6. Add Polish (T053-T063) → Final validation → **FEATURE COMPLETE** ✅

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T011)
2. Once Foundational is done:
   - Developer A: User Story 1 core (T012-T030)
   - Developer B: Wait for US1 classes, then start User Story 2 (T031-T040)
   - Developer C: Wait for US1 classes, then start User Story 3 (T041-T046)
3. Stories complete and integrate sequentially (US2 and US3 depend on US1 classes)

---

## Task Summary

**Total Tasks**: 63
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (User Story 1 - P1): 19 tasks 🎯 MVP
- Phase 4 (User Story 2 - P2): 10 tasks
- Phase 5 (User Story 3 - P3): 6 tasks
- Phase 6 (User Story 4 - P4): 6 tasks
- Phase 7 (Polish): 11 tasks

**Parallel Opportunities**: 20 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- **US1**: Launch → Add → View → Update → Delete → Mark Complete → Exit (Core CRUD)
- **US2**: Add varied todos → Filter by status/priority/tag → Verify results (Filtering)
- **US3**: Add todo with date/recurrence → View → Verify display (Date support)
- **US4**: Perform operations → View summary → Exit → Verify counts (Session tracking)

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 30 tasks

---

## Notes

- [P] tasks = different files or independent methods, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are not included per spec - can be added later if needed
- All file paths follow plan.md structure (src/models/, src/services/, src/cli/)
