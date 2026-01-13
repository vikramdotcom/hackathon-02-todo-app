# Implementation Plan: Phase II – Full-Stack Web Application

**Branch**: `002-phase-2-web-app` | **Date**: 2026-01-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-phase-2-web-app/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Phase II transforms the CLI todo application into a full-stack web application with user authentication, database persistence, and multi-user support. The implementation uses Next.js 14 for the frontend, FastAPI for the backend REST API, SQLModel for type-safe database operations, and Neon DB (PostgreSQL) for data persistence. The architecture maintains Phase I's canonical todo data model while adding user accounts, JWT-based authentication, and complete data isolation between users. All Phase I business logic semantics are preserved but implemented with database persistence instead of in-memory storage.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x with Next.js 14 (React 18)
- Backend: Python 3.13+

**Primary Dependencies**:
- Frontend: Next.js 14, React 18, Tailwind CSS 3.x, Axios for API calls
- Backend: FastAPI 0.104+, SQLModel 0.14+, Pydantic 2.x, python-jose for JWT, passlib for password hashing, psycopg2 for PostgreSQL

**Storage**:
- Database: Neon DB (PostgreSQL 15+)
- Session: JWT tokens (stateless authentication)

**Testing**:
- Backend: pytest with pytest-asyncio for async tests, httpx for API testing
- Frontend: Jest for unit tests, React Testing Library for component tests, Playwright for E2E tests

**Target Platform**:
- Web browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
- Responsive design for desktop, tablet, and mobile viewports

**Project Type**: Web application (separate frontend and backend)

**Performance Goals**:
- API response time: <500ms for CRUD operations (p95)
- Page load time: <2 seconds for todo list with 1000 items
- Support 100 concurrent authenticated users without degradation

**Constraints**:
- Stateless backend (all state in database, JWT tokens for auth)
- No modification to Phase I code
- Database schema must match Phase I data model semantics
- API must be consumable by Phase III AI agents

**Scale/Scope**:
- Multi-user support (100+ concurrent users)
- 1000+ todos per user without performance issues
- RESTful API with 15-20 endpoints
- 10-15 React components for frontend
- Database with 2 primary tables (users, todos)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Development (SDD) – Non-Negotiable
✅ **PASS** - All code will be generated from the Phase II specification. The spec defines 44 functional requirements, 5 user stories, and 10 success criteria. Implementation follows spec → plan → tasks → code workflow.

### II. Strict Data Model Compliance
✅ **PASS** - The canonical Todo schema from Phase I is preserved exactly:
- Same field names: id, title, description, completed, priority, tags, due_date, recurrence, created_at, updated_at
- Same types and validation rules
- Same default values
- Added user_id foreign key for multi-user support (extension, not modification)

### III. Phase Isolation & Forward Compatibility
✅ **PASS** - Phase II is architecturally independent:
- Phase I code remains unchanged and separate
- REST API designed for Phase III AI agent consumption
- Stateless architecture enables Phase IV Kubernetes deployment
- Database schema supports Phase V distributed deployment
- No breaking changes to Phase I contracts

### IV. Feature Completeness
✅ **PASS** - Every feature has:
- Clear intent: 5 prioritized user stories with business value
- Defined inputs/outputs: REST API contracts, web UI forms
- Explicit constraints: Performance goals, security requirements, scale limits
- Acceptance criteria: 10 measurable success criteria

### V. Code Generation & Validation
✅ **PASS** - Claude Code will generate all implementation code. Testing strategy defined with unit, integration, and E2E tests. Validation against spec requirements before deployment.

**Gate Status**: ✅ ALL GATES PASSED - Proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/002-phase-2-web-app/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-endpoints.md # REST API endpoint specifications
│   └── database-schema.md # Database table definitions
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phase-2-web-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # Configuration and environment variables
│   │   │   ├── security.py      # JWT token handling, password hashing
│   │   │   └── database.py      # Database connection and session management
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User SQLModel
│   │   │   └── todo.py          # Todo SQLModel
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User Pydantic schemas (request/response)
│   │   │   └── todo.py          # Todo Pydantic schemas (request/response)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py          # Dependency injection (get_db, get_current_user)
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py      # Authentication endpoints (register, login, logout)
│   │   │       ├── todos.py     # Todo CRUD endpoints
│   │   │       └── users.py     # User profile endpoints
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── auth_service.py  # Authentication business logic
│   │       ├── todo_service.py  # Todo business logic (Phase I semantics)
│   │       └── user_service.py  # User management business logic
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Pytest fixtures
│   │   ├── unit/
│   │   │   ├── test_auth_service.py
│   │   │   ├── test_todo_service.py
│   │   │   └── test_user_service.py
│   │   ├── integration/
│   │   │   ├── test_auth_api.py
│   │   │   ├── test_todos_api.py
│   │   │   └── test_users_api.py
│   │   └── e2e/
│   │       └── test_user_flows.py
│   ├── alembic/                 # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── app/                 # Next.js 14 app directory
    │   │   ├── layout.tsx       # Root layout
    │   │   ├── page.tsx         # Landing page
    │   │   ├── login/
    │   │   │   └── page.tsx     # Login page
    │   │   ├── register/
    │   │   │   └── page.tsx     # Registration page
    │   │   └── dashboard/
    │   │       ├── layout.tsx   # Dashboard layout (authenticated)
    │   │       ├── page.tsx     # Todo list page
    │   │       └── profile/
    │   │           └── page.tsx # User profile page
    │   ├── components/
    │   │   ├── auth/
    │   │   │   ├── LoginForm.tsx
    │   │   │   └── RegisterForm.tsx
    │   │   ├── todos/
    │   │   │   ├── TodoList.tsx
    │   │   │   ├── TodoItem.tsx
    │   │   │   ├── TodoForm.tsx
    │   │   │   └── TodoFilters.tsx
    │   │   ├── layout/
    │   │   │   ├── Header.tsx
    │   │   │   ├── Sidebar.tsx
    │   │   │   └── Footer.tsx
    │   │   └── ui/
    │   │       ├── Button.tsx
    │   │       ├── Input.tsx
    │   │       └── Modal.tsx
    │   ├── lib/
    │   │   ├── api.ts           # Axios API client
    │   │   ├── auth.ts          # Authentication utilities
    │   │   └── types.ts         # TypeScript type definitions
    │   └── styles/
    │       └── globals.css      # Tailwind CSS imports
    ├── tests/
    │   ├── unit/
    │   │   └── components/
    │   ├── integration/
    │   └── e2e/
    │       └── user-flows.spec.ts
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.js
    ├── next.config.js
    └── .env.local.example
```

**Structure Decision**: Web application structure with separate frontend and backend directories. Backend follows FastAPI best practices with layered architecture (models, schemas, services, API routes). Frontend uses Next.js 14 app directory structure with component-based organization. This separation enables independent development, testing, and deployment while maintaining clear API contracts between layers.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution gates passed. No complexity justification required.
