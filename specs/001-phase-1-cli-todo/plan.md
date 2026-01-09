# Implementation Plan: Phase I – In-Memory Python Console Todo App

**Branch**: `001-phase-1-cli-todo` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase-1-cli-todo/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Phase I delivers a menu-driven Python CLI application for managing todos in memory. The application implements the canonical Todo data model with full CRUD operations, filtering by status/priority/tags, and session tracking. Architecture follows a three-layer pattern: Domain (Todo model), Service (TodoManager for business logic), and Interface (CLI menu). All data is stored in-memory using Python standard library data structures. The implementation prioritizes correctness, input validation, and user experience with clear error messages and re-prompting on invalid input.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Python Standard Library only (no third-party packages)
**Storage**: In-memory only (Python lists and dictionaries)
**Testing**: unittest (Python standard library) for unit and integration tests
**Target Platform**: Cross-platform (any OS with Python 3.13+: Windows, macOS, Linux)
**Project Type**: Single project (CLI application)
**Performance Goals**: Not critical for Phase I; prioritizes correctness and user experience over performance
**Constraints**: Single-user, single-session, no file I/O, no network access, stdin/stdout/stderr only
**Scale/Scope**: Prototype/proof-of-concept; in-memory storage limits practical use to ~1000 todos per session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development
✅ **PASS** - Feature specification (spec.md) is complete with clear intent, inputs/outputs, constraints, and acceptance criteria. All code will be generated from this specification.

### Principle II: Strict Data Model Compliance
✅ **PASS** - The canonical Todo schema is defined in spec.md (FR-001) with all required fields: id, title, description, completed, priority, tags, due_date, recurrence, created_at, updated_at. This schema is immutable and will be preserved across all phases.

### Principle III: Phase Isolation & Forward Compatibility
✅ **PASS** - Phase I architecture is independent. The three-layer design (Domain, Service, Interface) allows the Service layer to be reused in Phase II (Web API) without modification. The Todo model and operations are abstracted from the CLI interface.

### Principle IV: Feature Completeness
✅ **PASS** - Specification includes clear intent (menu-driven todo management), defined inputs/outputs (CLI menu options, todo fields), explicit constraints (in-memory only, single-user, Python 3.13+), and acceptance criteria (SC-001 through SC-007).

### Principle V: Code Generation & Validation
✅ **PASS** - Implementation will be validated against spec.md acceptance criteria. Test cases are derived from user scenarios and functional requirements. Any divergence will be resolved by refining the spec, not ad-hoc code changes.

**Gate Status**: ✅ ALL CHECKS PASSED - Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-1-cli-todo/
├── spec.md              # Feature specification (already exists)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── cli-interface.md # CLI menu contract and interaction patterns
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   └── todo.py          # Todo domain model (dataclass with validation)
├── services/
│   └── todo_service.py  # TodoManager service (business logic, CRUD, filtering)
├── cli/
│   └── menu.py          # CLI menu interface (user interaction, input/output)
└── main.py              # Application entry point

tests/
├── unit/
│   ├── test_todo_model.py      # Todo model validation, field constraints
│   ├── test_todo_service.py    # TodoManager CRUD operations, filtering logic
│   └── test_cli_menu.py        # CLI menu input validation, display formatting
└── integration/
    └── test_end_to_end.py      # Full user journeys (add → view → update → delete)

README.md                # Project overview and setup instructions
requirements.txt         # Empty (no third-party dependencies)
.gitignore              # Python standard ignores
```

**Structure Decision**: Single project structure selected. This is a standalone CLI application with no web frontend or mobile components. The three-layer architecture (Domain → Service → Interface) maps cleanly to the src/ subdirectories. Tests are organized by scope (unit vs integration) rather than by layer, following Python testing conventions. The Service layer (todo_service.py) is designed to be reusable in Phase II when exposing a REST API.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All constitution principles are satisfied.

---

## Phase 0: Research Outputs

**Status**: ✅ Complete

**Artifacts Generated**:
- `research.md`: Technical decisions and rationale for all technology choices

**Key Decisions**:
1. Python 3.13+ with standard library only
2. In-memory storage using Python lists and dictionaries
3. Three-layer architecture (Domain, Service, Interface)
4. unittest for testing framework
5. ISO 8601 datetime handling
6. Menu-driven CLI with input validation and re-prompting

**Unknowns Resolved**: All technical context items were explicitly specified in spec.md. No open research questions required resolution.

---

## Phase 1: Design & Contracts Outputs

**Status**: ✅ Complete

**Artifacts Generated**:
1. `data-model.md`: Canonical Todo schema with validation rules, Session entity, data flow diagrams
2. `contracts/cli-interface.md`: Complete CLI interface contract with menu structure, operation contracts, I/O protocol, error handling
3. `quickstart.md`: User guide with installation, tutorial, troubleshooting, and testing instructions
4. `CLAUDE.md`: Updated agent context with Python 3.13+, standard library, in-memory storage

**Design Highlights**:
- **Todo Model**: 10 fields (id, title, description, completed, priority, tags, due_date, recurrence, created_at, updated_at)
- **Validation**: Title required (1-10,000 chars), priority enum (low/medium/high), timestamps immutable
- **CLI Operations**: 9 menu options covering full CRUD, filtering, session tracking
- **Error Handling**: Graceful validation with clear messages and re-prompting
- **Forward Compatibility**: Service layer designed for reuse in Phase II REST API

---

## Constitution Check (Post-Design Re-evaluation)

*GATE: Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development
✅ **PASS** - All design artifacts (data-model.md, cli-interface.md, quickstart.md) are derived directly from spec.md. No ad-hoc design decisions made.

### Principle II: Strict Data Model Compliance
✅ **PASS** - The canonical Todo schema in data-model.md matches spec.md (FR-001) exactly. All 10 fields are defined with correct types and constraints. Schema is documented as immutable across all phases.

### Principle III: Phase Isolation & Forward Compatibility
✅ **PASS** - Design maintains phase isolation. Service layer (TodoManager) is abstracted from CLI interface, enabling reuse in Phase II. Data model includes forward compatibility notes for Phases II-V.

### Principle IV: Feature Completeness
✅ **PASS** - Design artifacts include clear contracts (CLI interface), explicit constraints (validation rules), and testable acceptance criteria (operation postconditions).

### Principle V: Code Generation & Validation
✅ **PASS** - Design provides complete specifications for code generation. Test coverage is defined in cli-interface.md and quickstart.md. All operations have defined inputs, outputs, and error cases.

**Gate Status**: ✅ ALL CHECKS PASSED - Design is complete and compliant.

---

## Next Steps

**Phase 2: Task Generation** (NOT part of /sp.plan command)

Run `/sp.tasks` to generate `tasks.md` with:
- Dependency-ordered implementation tasks
- Test cases for each task
- Acceptance criteria and validation steps

**Implementation Workflow**:
1. Review and approve this plan
2. Run `/sp.tasks` to generate actionable tasks
3. Execute tasks in dependency order
4. Validate against acceptance criteria (SC-001 through SC-007)
5. Run full test suite before marking feature complete

---

## Summary

Phase I planning is complete. All design artifacts have been generated and validated against the constitution. The architecture is simple (three-layer pattern), forward-compatible (service layer reusable in Phase II), and fully specified (data model, CLI contract, quickstart guide). No complexity violations or open questions remain.

**Branch**: `001-phase-1-cli-todo`
**Plan Document**: `specs/001-phase-1-cli-todo/plan.md`
**Generated Artifacts**:
- `research.md` (Phase 0)
- `data-model.md` (Phase 1)
- `contracts/cli-interface.md` (Phase 1)
- `quickstart.md` (Phase 1)
- Updated `CLAUDE.md` (agent context)

**Status**: ✅ Ready for task generation (`/sp.tasks`)
