# Tasks: Phase II – Full-Stack Web Application

**Input**: Design documents from `/specs/002-phase-2-web-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification. Tests can be added later if needed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase-2-web-app/backend/app/`
- **Frontend**: `phase-2-web-app/frontend/src/`
- Paths shown below follow the web application structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure per plan.md in phase-2-web-app/backend/
- [ ] T002 Initialize Python project with requirements.txt (FastAPI, SQLModel, Pydantic, python-jose, passlib, psycopg2, uvicorn, alembic)
- [ ] T003 Create frontend directory structure per plan.md in phase-2-web-app/frontend/
- [ ] T004 Initialize Next.js 14 project with TypeScript and Tailwind CSS in phase-2-web-app/frontend/
- [ ] T005 [P] Create backend .env.example with DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
- [ ] T006 [P] Create frontend .env.local.example with NEXT_PUBLIC_API_URL
- [ ] T007 [P] Configure ESLint and Prettier for frontend in phase-2-web-app/frontend/
- [ ] T008 [P] Configure pytest and pytest-asyncio for backend in phase-2-web-app/backend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Create database configuration in phase-2-web-app/backend/app/core/config.py (load env vars, database URL, JWT settings)
- [ ] T010 Create database connection manager in phase-2-web-app/backend/app/core/database.py (SQLModel engine, session factory)
- [ ] T011 Initialize Alembic for database migrations in phase-2-web-app/backend/alembic/
- [ ] T012 Create initial migration (001_initial_schema) for users and todos tables in phase-2-web-app/backend/alembic/versions/
- [ ] T013 [P] Create security utilities in phase-2-web-app/backend/app/core/security.py (password hashing, JWT token generation/validation)
- [ ] T014 [P] Create FastAPI main application in phase-2-web-app/backend/app/main.py (app initialization, CORS, middleware)
- [ ] T015 [P] Create API router structure in phase-2-web-app/backend/app/api/routes/__init__.py
- [ ] T016 [P] Create dependency injection utilities in phase-2-web-app/backend/app/api/deps.py (get_db, get_current_user)
- [ ] T017 [P] Create base Pydantic schemas in phase-2-web-app/backend/app/schemas/__init__.py
- [ ] T018 [P] Create Axios API client in phase-2-web-app/frontend/src/lib/api.ts (base URL, interceptors, error handling)
- [ ] T019 [P] Create authentication utilities in phase-2-web-app/frontend/src/lib/auth.ts (token storage, auth state management)
- [ ] T020 [P] Create TypeScript type definitions in phase-2-web-app/frontend/src/lib/types.ts (User, Todo, API response types)
- [ ] T021 [P] Create root layout in phase-2-web-app/frontend/src/app/layout.tsx (HTML structure, metadata, global styles)
- [ ] T022 [P] Create landing page in phase-2-web-app/frontend/src/app/page.tsx (welcome page with login/register links)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to register accounts, log in with credentials, and maintain secure authenticated sessions

**Independent Test**: (1) Visit registration page, (2) create account with email/username/password, (3) log in with credentials, (4) verify access to dashboard, (5) log out successfully

### Backend Implementation for User Story 1

- [ ] T023 [P] [US1] Create User SQLModel in phase-2-web-app/backend/app/models/user.py (id, email, username, hashed_password, created_at, updated_at)
- [ ] T024 [P] [US1] Create User Pydantic schemas in phase-2-web-app/backend/app/schemas/user.py (UserCreate, UserLogin, UserResponse, Token)
- [ ] T025 [US1] Create AuthService in phase-2-web-app/backend/app/services/auth_service.py (register_user, authenticate_user, create_access_token)
- [ ] T026 [US1] Create UserService in phase-2-web-app/backend/app/services/user_service.py (get_user_by_email, get_user_by_id, update_user)
- [ ] T027 [US1] Implement POST /auth/register endpoint in phase-2-web-app/backend/app/api/routes/auth.py
- [ ] T028 [US1] Implement POST /auth/login endpoint in phase-2-web-app/backend/app/api/routes/auth.py
- [ ] T029 [US1] Implement POST /auth/logout endpoint in phase-2-web-app/backend/app/api/routes/auth.py
- [ ] T030 [US1] Implement GET /auth/me endpoint in phase-2-web-app/backend/app/api/routes/auth.py
- [ ] T031 [US1] Add authentication routes to main router in phase-2-web-app/backend/app/main.py

### Frontend Implementation for User Story 1

- [ ] T032 [P] [US1] Create RegisterForm component in phase-2-web-app/frontend/src/components/auth/RegisterForm.tsx (email, username, password inputs, validation)
- [ ] T033 [P] [US1] Create LoginForm component in phase-2-web-app/frontend/src/components/auth/LoginForm.tsx (email, password inputs, validation)
- [ ] T034 [P] [US1] Create registration page in phase-2-web-app/frontend/src/app/register/page.tsx (render RegisterForm, handle submission)
- [ ] T035 [P] [US1] Create login page in phase-2-web-app/frontend/src/app/login/page.tsx (render LoginForm, handle submission)
- [ ] T036 [US1] Create dashboard layout in phase-2-web-app/frontend/src/app/dashboard/layout.tsx (authenticated layout with header, navigation)
- [ ] T037 [US1] Create dashboard page in phase-2-web-app/frontend/src/app/dashboard/page.tsx (placeholder for todo list)
- [ ] T038 [US1] Add authentication state management and protected route logic in phase-2-web-app/frontend/src/lib/auth.ts
- [ ] T039 [US1] Create Header component in phase-2-web-app/frontend/src/components/layout/Header.tsx (logo, user menu, logout button)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, login, and logout

---

## Phase 4: User Story 2 - Web-Based Todo Management (Priority: P2)

**Goal**: Enable authenticated users to create, view, update, delete, and manage todos through web interface

**Independent Test**: (1) Log in as user, (2) create new todo via form, (3) view todo list, (4) update todo, (5) mark complete, (6) delete todo - all operations persist

### Backend Implementation for User Story 2

- [ ] T040 [P] [US2] Create Todo SQLModel in phase-2-web-app/backend/app/models/todo.py (id, user_id, title, description, completed, priority, tags, due_date, recurrence, created_at, updated_at)
- [ ] T041 [P] [US2] Create Todo Pydantic schemas in phase-2-web-app/backend/app/schemas/todo.py (TodoCreate, TodoUpdate, TodoResponse, TodoList)
- [ ] T042 [US2] Create TodoService in phase-2-web-app/backend/app/services/todo_service.py (create_todo, get_todos, get_todo_by_id, update_todo, delete_todo, toggle_complete)
- [ ] T043 [US2] Implement GET /todos endpoint in phase-2-web-app/backend/app/api/routes/todos.py (list todos with filtering by status, priority, tag)
- [ ] T044 [US2] Implement GET /todos/{id} endpoint in phase-2-web-app/backend/app/api/routes/todos.py
- [ ] T045 [US2] Implement POST /todos endpoint in phase-2-web-app/backend/app/api/routes/todos.py
- [ ] T046 [US2] Implement PUT /todos/{id} endpoint in phase-2-web-app/backend/app/api/routes/todos.py
- [ ] T047 [US2] Implement PATCH /todos/{id} endpoint in phase-2-web-app/backend/app/api/routes/todos.py
- [ ] T048 [US2] Implement DELETE /todos/{id} endpoint in phase-2-web-app/backend/app/api/routes/todos.py
- [ ] T049 [US2] Implement PATCH /todos/{id}/complete endpoint in phase-2-web-app/backend/app/api/routes/todos.py
- [ ] T050 [US2] Implement PATCH /todos/{id}/incomplete endpoint in phase-2-web-app/backend/app/api/routes/todos.py
- [ ] T051 [US2] Add todo routes to main router in phase-2-web-app/backend/app/main.py

### Frontend Implementation for User Story 2

- [ ] T052 [P] [US2] Create TodoList component in phase-2-web-app/frontend/src/components/todos/TodoList.tsx (display todos, handle empty state)
- [ ] T053 [P] [US2] Create TodoItem component in phase-2-web-app/frontend/src/components/todos/TodoItem.tsx (display single todo, complete checkbox, edit/delete buttons)
- [ ] T054 [P] [US2] Create TodoForm component in phase-2-web-app/frontend/src/components/todos/TodoForm.tsx (create/edit form with title, description, priority, tags, due date)
- [ ] T055 [P] [US2] Create TodoFilters component in phase-2-web-app/frontend/src/components/todos/TodoFilters.tsx (filter by status, priority, tag)
- [ ] T056 [US2] Update dashboard page in phase-2-web-app/frontend/src/app/dashboard/page.tsx (render TodoList, TodoFilters, add todo button)
- [ ] T057 [US2] Create Modal component in phase-2-web-app/frontend/src/components/ui/Modal.tsx (reusable modal for todo form)
- [ ] T058 [US2] Add todo API functions in phase-2-web-app/frontend/src/lib/api.ts (getTodos, createTodo, updateTodo, deleteTodo, toggleComplete)
- [ ] T059 [US2] Implement todo state management and CRUD operations in dashboard page

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can manage todos through web interface

---

## Phase 5: User Story 3 - Persistent Data and Cross-Device Access (Priority: P3)

**Goal**: Ensure todos persist in database and are accessible from any device

**Independent Test**: (1) Log in from one browser, (2) create todos, (3) log out, (4) log in from different browser, (5) verify todos are present

**Note**: This user story is implicitly satisfied by User Stories 1 and 2 (authentication + database persistence). No additional implementation tasks required beyond validation.

### Validation for User Story 3

- [ ] T060 [US3] Verify database persistence by testing cross-session access in phase-2-web-app/backend/ (manual validation)
- [ ] T061 [US3] Verify cross-device access by testing from multiple browsers (manual validation)
- [ ] T062 [US3] Add database connection error handling in phase-2-web-app/backend/app/core/database.py

**Checkpoint**: User Story 3 validated - data persists across sessions and devices

---

## Phase 6: User Story 4 - User Profile and Statistics Dashboard (Priority: P4)

**Goal**: Enable users to view profile information and todo statistics

**Independent Test**: (1) Log in with existing todos, (2) navigate to profile page, (3) verify accurate statistics (total, completed, completion rate, priority distribution)

### Backend Implementation for User Story 4

- [ ] T063 [P] [US4] Create User statistics schema in phase-2-web-app/backend/app/schemas/user.py (UserStats with total_todos, completed_todos, completion_rate, todos_by_priority)
- [ ] T064 [US4] Add get_user_stats method to UserService in phase-2-web-app/backend/app/services/user_service.py
- [ ] T065 [US4] Implement GET /users/me endpoint in phase-2-web-app/backend/app/api/routes/users.py
- [ ] T066 [US4] Implement PUT /users/me endpoint in phase-2-web-app/backend/app/api/routes/users.py (update username, email)
- [ ] T067 [US4] Implement GET /users/me/stats endpoint in phase-2-web-app/backend/app/api/routes/users.py
- [ ] T068 [US4] Add user routes to main router in phase-2-web-app/backend/app/main.py

### Frontend Implementation for User Story 4

- [ ] T069 [P] [US4] Create profile page in phase-2-web-app/frontend/src/app/dashboard/profile/page.tsx (display user info, statistics)
- [ ] T070 [P] [US4] Create ProfileForm component in phase-2-web-app/frontend/src/components/auth/ProfileForm.tsx (edit username, email)
- [ ] T071 [P] [US4] Create StatsCard component in phase-2-web-app/frontend/src/components/ui/StatsCard.tsx (display statistics with icons)
- [ ] T072 [US4] Add user API functions in phase-2-web-app/frontend/src/lib/api.ts (getProfile, updateProfile, getStats)
- [ ] T073 [US4] Add profile link to Header navigation in phase-2-web-app/frontend/src/components/layout/Header.tsx

**Checkpoint**: User Story 4 complete - users can view profile and statistics

---

## Phase 7: User Story 5 - Advanced Filtering and Search (Priority: P5)

**Goal**: Enable users to search todos by keyword and apply multiple filters simultaneously

**Independent Test**: (1) Create multiple todos with various attributes, (2) use search box, (3) apply multiple filters, (4) sort by different fields

### Backend Implementation for User Story 5

- [ ] T074 [US5] Add search parameter to GET /todos endpoint in phase-2-web-app/backend/app/api/routes/todos.py (search in title and description)
- [ ] T075 [US5] Add multiple filter support to TodoService in phase-2-web-app/backend/app/services/todo_service.py (combine status, priority, tag filters)
- [ ] T076 [US5] Add sorting parameters to GET /todos endpoint in phase-2-web-app/backend/app/api/routes/todos.py (sort_by, sort_order)
- [ ] T077 [US5] Add pagination support to GET /todos endpoint in phase-2-web-app/backend/app/api/routes/todos.py (limit, offset)

### Frontend Implementation for User Story 5

- [ ] T078 [P] [US5] Create SearchBar component in phase-2-web-app/frontend/src/components/todos/SearchBar.tsx (search input with debounce)
- [ ] T079 [P] [US5] Create SortControls component in phase-2-web-app/frontend/src/components/todos/SortControls.tsx (sort by field and direction)
- [ ] T080 [US5] Update TodoFilters component in phase-2-web-app/frontend/src/components/todos/TodoFilters.tsx (support multiple simultaneous filters)
- [ ] T081 [US5] Add search and advanced filtering to dashboard page in phase-2-web-app/frontend/src/app/dashboard/page.tsx
- [ ] T082 [US5] Add pagination controls to TodoList component in phase-2-web-app/frontend/src/components/todos/TodoList.tsx

**Checkpoint**: All user stories complete - full feature set implemented

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T083 [P] Create Button component in phase-2-web-app/frontend/src/components/ui/Button.tsx (reusable styled button)
- [ ] T084 [P] Create Input component in phase-2-web-app/frontend/src/components/ui/Input.tsx (reusable styled input)
- [ ] T085 [P] Add loading states to all API calls in phase-2-web-app/frontend/src/lib/api.ts
- [ ] T086 [P] Add error handling and user-friendly error messages across all components
- [ ] T087 [P] Add success notifications for CRUD operations in phase-2-web-app/frontend/src/components/ui/
- [ ] T088 [P] Implement responsive design for mobile devices across all components
- [ ] T089 [P] Add dark mode support using Tailwind CSS in phase-2-web-app/frontend/src/app/layout.tsx
- [ ] T090 [P] Add input validation and error messages to all forms
- [ ] T091 [P] Add rate limiting to authentication endpoints in phase-2-web-app/backend/app/api/routes/auth.py
- [ ] T092 [P] Add API documentation comments for OpenAPI/Swagger in phase-2-web-app/backend/app/api/routes/
- [ ] T093 [P] Create Footer component in phase-2-web-app/frontend/src/components/layout/Footer.tsx
- [ ] T094 [P] Add accessibility attributes (ARIA labels) to all interactive components
- [ ] T095 Validate quickstart.md by following setup instructions in phase-2-web-app/
- [ ] T096 Run database migrations and verify schema in phase-2-web-app/backend/
- [ ] T097 Test end-to-end user flows for all user stories
- [ ] T098 Performance optimization: Add database indexes per database-schema.md
- [ ] T099 Security review: Verify input sanitization and SQL injection prevention
- [ ] T100 Code cleanup and remove any TODO comments

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Depends on User Story 1 (needs authentication)
  - User Story 3 (P3): Validation only - Depends on User Stories 1 and 2
  - User Story 4 (P4): Can start after Foundational - Depends on User Stories 1 and 2 (needs auth and todos)
  - User Story 5 (P5): Can start after Foundational - Depends on User Story 2 (extends todo functionality)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - Can start after Foundational
- **User Story 2 (P2)**: Depends on User Story 1 (requires authentication)
- **User Story 3 (P3)**: Depends on User Stories 1 and 2 (validation of persistence)
- **User Story 4 (P4)**: Depends on User Stories 1 and 2 (requires auth and todos)
- **User Story 5 (P5)**: Depends on User Story 2 (extends todo functionality)

### Within Each User Story

- Backend models before services
- Services before API endpoints
- API endpoints before frontend components
- Core components before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T005, T006, T007, T008)
- All Foundational tasks marked [P] can run in parallel after T009-T012 complete (T013-T022)
- Within User Story 1: T023-T024 (models/schemas) can run in parallel, T032-T035 (frontend forms/pages) can run in parallel
- Within User Story 2: T040-T041 (models/schemas) can run in parallel, T052-T055 (frontend components) can run in parallel
- Within User Story 4: T063-T064 can run in parallel, T069-T071 can run in parallel
- Within User Story 5: T078-T079 can run in parallel
- All Polish tasks marked [P] can run in parallel (T083-T094)

---

## Parallel Example: User Story 1

```bash
# Launch backend models and schemas together:
Task T023: "Create User SQLModel in phase-2-web-app/backend/app/models/user.py"
Task T024: "Create User Pydantic schemas in phase-2-web-app/backend/app/schemas/user.py"

# Launch frontend forms and pages together:
Task T032: "Create RegisterForm component in phase-2-web-app/frontend/src/components/auth/RegisterForm.tsx"
Task T033: "Create LoginForm component in phase-2-web-app/frontend/src/components/auth/LoginForm.tsx"
Task T034: "Create registration page in phase-2-web-app/frontend/src/app/register/page.tsx"
Task T035: "Create login page in phase-2-web-app/frontend/src/app/login/page.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch backend models and schemas together:
Task T040: "Create Todo SQLModel in phase-2-web-app/backend/app/models/todo.py"
Task T041: "Create Todo Pydantic schemas in phase-2-web-app/backend/app/schemas/todo.py"

# Launch frontend components together:
Task T052: "Create TodoList component in phase-2-web-app/frontend/src/components/todos/TodoList.tsx"
Task T053: "Create TodoItem component in phase-2-web-app/frontend/src/components/todos/TodoItem.tsx"
Task T054: "Create TodoForm component in phase-2-web-app/frontend/src/components/todos/TodoForm.tsx"
Task T055: "Create TodoFilters component in phase-2-web-app/frontend/src/components/todos/TodoFilters.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 and 2 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T022) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T023-T039) - Authentication
4. Complete Phase 4: User Story 2 (T040-T059) - Todo Management
5. **STOP and VALIDATE**: Test User Stories 1 and 2 independently
6. Deploy/demo MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Authentication MVP)
3. Add User Story 2 → Test independently → Deploy/Demo (Full Todo App MVP)
4. Add User Story 3 → Validate persistence → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo (Profile & Stats)
6. Add User Story 5 → Test independently → Deploy/Demo (Advanced Features)
7. Add Polish → Final release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T022)
2. Once Foundational is done:
   - Developer A: User Story 1 (T023-T039)
   - Developer B: Start User Story 2 backend (T040-T042) - wait for US1 auth
3. After User Story 1 completes:
   - Developer A: User Story 4 (T063-T073)
   - Developer B: Complete User Story 2 (T043-T059)
   - Developer C: User Story 5 (T074-T082)
4. All developers: Polish tasks (T083-T100) in parallel

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- User Story 3 is primarily validation as persistence is built into US1+US2
- User Stories 4 and 5 can be implemented in parallel after US1+US2 complete
- Polish phase tasks can mostly run in parallel
- Total: 100 tasks across 8 phases
