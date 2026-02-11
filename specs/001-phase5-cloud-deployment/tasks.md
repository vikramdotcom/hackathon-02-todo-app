# Implementation Tasks: Phase V - Cloud-Native Event-Driven Todo System

**Feature**: Phase V - Cloud-Native Event-Driven Architecture
**Branch**: `001-phase5-cloud-deployment`
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)
**Generated**: 2026-02-10

## Overview

This document contains actionable implementation tasks for Phase V, organized by user story to enable independent testing and incremental delivery. Each user story can be implemented and tested independently, allowing for parallel development and early value delivery.

**Total Estimated Effort**: 35-60 hours
**Target Timeline**: 4-6 weeks (part-time development)

## Task Summary

- **Phase 1 (Setup)**: 8 tasks - Project initialization and infrastructure setup
- **Phase 2 (Foundational)**: 12 tasks - Blocking prerequisites for all user stories
- **Phase 3 (US1 - Recurring Tasks)**: 15 tasks - P1 feature, core differentiator
- **Phase 4 (US2 - Due Dates & Reminders)**: 12 tasks - P1 feature, time management
- **Phase 5 (US3 - Priorities & Tags)**: 8 tasks - P2 feature, organization
- **Phase 6 (US4 - Search & Filter)**: 10 tasks - P2 feature, productivity
- **Phase 7 (US5 - Real-Time Sync)**: 14 tasks - P2 feature, modern UX
- **Phase 8 (US6 - Audit Trail)**: 8 tasks - P3 feature, accountability
- **Phase 9 (US7 - Automated Deployment)**: 10 tasks - P3 feature, CI/CD
- **Phase 10 (Polish)**: 8 tasks - Cross-cutting concerns and documentation

**Total Tasks**: 105

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
- **Phase 1**: Setup (required)
- **Phase 2**: Foundational (required)
- **Phase 3**: User Story 1 - Recurring Tasks (P1, core differentiator)

This MVP delivers immediate value with recurring task functionality, the most requested feature.

### Incremental Delivery
After MVP, implement user stories in priority order:
1. **Phase 4**: US2 - Due Dates & Reminders (P1)
2. **Phase 5**: US3 - Priorities & Tags (P2)
3. **Phase 6**: US4 - Search & Filter (P2)
4. **Phase 7**: US5 - Real-Time Sync (P2)
5. **Phase 8**: US6 - Audit Trail (P3)
6. **Phase 9**: US7 - Automated Deployment (P3)
7. **Phase 10**: Polish & Documentation

### Parallel Execution Opportunities
Tasks marked with `[P]` can be executed in parallel with other `[P]` tasks in the same phase, as they work on different files or have no dependencies.

---

## Phase 1: Setup & Infrastructure (1-2 hours)

**Goal**: Initialize project structure, setup development environment, and prepare infrastructure components.

**Deliverables**: Project structure created, Helm charts ready, development environment configured.

### Tasks

- [x] T001 Create phase-5-cloud-deployment folder structure per implementation plan
- [x] T002 Copy Phase IV Helm charts to phase-5-cloud-deployment/helm/todo-chatbot/
- [x] T003 Create backend service structure in phase-5-cloud-deployment/backend/
- [x] T004 Create microservices structure in phase-5-cloud-deployment/services/
- [x] T005 Create frontend structure in phase-5-cloud-deployment/frontend/
- [x] T006 Create k8s manifests structure in phase-5-cloud-deployment/k8s/
- [x] T007 Create scripts folder in phase-5-cloud-deployment/scripts/
- [x] T008 Update main README.md with Phase V section and architecture overview

---

## Phase 2: Foundational Infrastructure (4-6 hours)

**Goal**: Setup blocking prerequisites that all user stories depend on - Redpanda Cloud, Dapr, database extensions, and base API structure.

**Deliverables**: Event streaming ready, Dapr configured, database schema extended, API v2 structure created.

**Blocking**: Must complete before any user story implementation.

### Tasks

- [ ] T009 Sign up for Redpanda Cloud serverless tier and create cluster
- [ ] T010 Create Redpanda topics: task-events, reminders, task-updates
- [ ] T011 Configure SASL authentication for Redpanda and store credentials
- [ ] T012 Test Redpanda connection with Python producer/consumer script
- [ ] T013 Install Dapr CLI locally and initialize in Minikube (dapr init -k)
- [ ] T014 Create Dapr component: kafka-pubsub.yaml in k8s/dapr-components/
- [ ] T015 Create Dapr component: statestore.yaml in k8s/dapr-components/
- [ ] T016 Create Dapr component: reminder-cron.yaml in k8s/dapr-components/
- [ ] T017 Create Dapr component: k8s-secrets.yaml in k8s/dapr-components/
- [ ] T018 Apply Dapr components to Minikube and verify with dapr dashboard
- [ ] T019 Create API v2 structure in backend/app/api/v2/ for new endpoints
- [ ] T020 Add Dapr SDK to backend dependencies in backend/requirements.txt

---

## Phase 3: User Story 1 - Recurring Tasks (P1) (8-12 hours)

**User Story**: A user needs to set up recurring tasks (daily standup, weekly reports, monthly reviews) that automatically regenerate after completion.

**Independent Test**: Create a daily recurring task, mark it complete, verify new instance created for next day.

**Value**: Core differentiator, most requested feature, immediate value for repetitive workflows.

### Backend Tasks

- [ ] T021 [P] [US1] Create RecurrencePattern model in backend/app/models/recurrence.py
- [ ] T022 [P] [US1] Extend Todo model with recurrence_pattern field in backend/app/models/todo.py
- [ ] T023 [US1] Create Alembic migration 005_add_recurrence_fields.py in backend/migrations/versions/
- [ ] T024 [US1] Run migration to add recurrence fields to database
- [ ] T025 [P] [US1] Create RecurrenceService in backend/app/services/recurrence_service.py
- [ ] T026 [US1] Extend TodoService with recurrence logic in backend/app/services/todo_service.py
- [ ] T027 [US1] Update POST /api/v2/todos endpoint to accept recurrence in backend/app/api/v2/todos.py
- [ ] T028 [US1] Update GET /api/v2/todos endpoint to return recurrence in backend/app/api/v2/todos.py
- [ ] T029 [US1] Add recurrence validation logic in backend/app/api/v2/todos.py

### Microservice Tasks

- [ ] T030 [P] [US1] Create recurring-task-service structure in services/recurring-task-service/
- [ ] T031 [P] [US1] Implement recurrence engine in services/recurring-task-service/app/recurrence_engine.py
- [ ] T032 [US1] Implement Dapr subscriber in services/recurring-task-service/app/dapr_subscriber.py
- [ ] T033 [US1] Implement main service logic in services/recurring-task-service/app/main.py
- [ ] T034 [US1] Create Dockerfile for recurring-task-service in services/recurring-task-service/

### Frontend Tasks

- [ ] T035 [P] [US1] Create RecurrenceSelector component in frontend/src/components/todos/RecurrenceSelector.tsx
- [ ] T036 [US1] Extend TodoForm with recurrence selector in frontend/src/components/todos/TodoForm.tsx
- [ ] T037 [US1] Update TodoList to display recurrence indicator in frontend/src/components/todos/TodoList.tsx
- [ ] T038 [US1] Extend useTodos hook with recurrence support in frontend/src/hooks/useTodos.ts
- [ ] T039 [US1] Update API client with recurrence fields in frontend/src/services/api.ts

### Chatbot Tasks

- [ ] T040 [P] [US1] Update LLM system prompt with recurrence commands in backend/app/chat/services/llm_service.py
- [ ] T041 [US1] Extend create_todo function schema with recurrence in backend/app/chat/services/llm_service.py

### Deployment Tasks

- [ ] T042 [US1] Add recurring-service to Helm chart in helm/todo-chatbot/templates/recurring-service/
- [ ] T043 [US1] Update Helm values with recurring-service config in helm/todo-chatbot/values.yaml
- [ ] T044 [US1] Deploy to Minikube and test recurring task creation and regeneration

**Acceptance Test**: Create daily recurring task → mark complete → verify new instance created with next day's date

---

## Phase 4: User Story 2 - Due Dates & Reminders (P1) (6-10 hours)

**User Story**: A user needs to assign due dates to tasks and receive timely reminders (10 minutes, 1 hour, 1 day before).

**Independent Test**: Create task with due date and multiple reminder offsets, verify reminders triggered at correct times.

**Value**: Essential time management, directly impacts productivity.

### Backend Tasks

- [ ] T045 [P] [US2] Create Reminder model in backend/app/models/reminder.py
- [ ] T046 [P] [US2] Extend Todo model with due_date and reminder_offsets in backend/app/models/todo.py
- [ ] T047 [US2] Create Alembic migration 006_add_due_date_reminders.py in backend/migrations/versions/
- [ ] T048 [US2] Run migration to add due date and reminder fields
- [ ] T049 [P] [US2] Create ReminderService in backend/app/services/reminder_service.py
- [ ] T050 [US2] Extend TodoService with reminder logic in backend/app/services/todo_service.py
- [ ] T051 [US2] Update POST /api/v2/todos to accept due_date and reminders in backend/app/api/v2/todos.py
- [ ] T052 [US2] Add reminder cancellation on task completion in backend/app/services/todo_service.py

### Microservice Tasks

- [ ] T053 [P] [US2] Create notification-service structure in services/notification-service/
- [ ] T054 [P] [US2] Implement scheduler in services/notification-service/app/scheduler.py
- [ ] T055 [P] [US2] Implement notifier in services/notification-service/app/notifier.py
- [ ] T056 [US2] Implement Dapr subscriber and cron binding in services/notification-service/app/dapr_subscriber.py
- [ ] T057 [US2] Implement main service logic in services/notification-service/app/main.py
- [ ] T058 [US2] Create Dockerfile for notification-service in services/notification-service/

### Frontend Tasks

- [ ] T059 [P] [US2] Add due date picker to TodoForm in frontend/src/components/todos/TodoForm.tsx
- [ ] T060 [P] [US2] Add reminder offset selector to TodoForm in frontend/src/components/todos/TodoForm.tsx
- [ ] T061 [US2] Update TodoList to highlight overdue tasks in frontend/src/components/todos/TodoList.tsx
- [ ] T062 [US2] Update API client with due_date and reminders in frontend/src/services/api.ts

### Deployment Tasks

- [ ] T063 [US2] Add notification-service to Helm chart in helm/todo-chatbot/templates/notification-service/
- [ ] T064 [US2] Update Helm values with notification-service config in helm/todo-chatbot/values.yaml
- [ ] T065 [US2] Deploy to Minikube and test reminder triggering

**Acceptance Test**: Create task with due date + 3 reminder offsets → verify reminders triggered at correct times

---

## Phase 5: User Story 3 - Priorities & Tags (P2) (4-6 hours)

**User Story**: A user needs to categorize tasks by priority (low/medium/high/urgent) and apply multiple tags.

**Independent Test**: Create tasks with different priorities and tags, filter and sort by these attributes.

**Value**: Organization and focus, essential for managing multiple projects.

### Backend Tasks

- [ ] T066 [P] [US3] Extend Todo model with priority and tags fields in backend/app/models/todo.py
- [ ] T067 [US3] Create Alembic migration 007_add_priority_tags.py in backend/migrations/versions/
- [ ] T068 [US3] Run migration to add priority and tags fields
- [ ] T069 [US3] Update POST /api/v2/todos to accept priority and tags in backend/app/api/v2/todos.py
- [ ] T070 [US3] Add priority validation (low/medium/high/urgent) in backend/app/api/v2/todos.py
- [ ] T071 [US3] Implement sort by priority in TodoService in backend/app/services/todo_service.py
- [ ] T072 [US3] Implement filter by tags in TodoService in backend/app/services/todo_service.py

### Frontend Tasks

- [ ] T073 [P] [US3] Add priority dropdown to TodoForm in frontend/src/components/todos/TodoForm.tsx
- [ ] T074 [P] [US3] Add tag input with chips to TodoForm in frontend/src/components/todos/TodoForm.tsx
- [ ] T075 [US3] Add priority visual indicators to TodoList in frontend/src/components/todos/TodoList.tsx
- [ ] T076 [US3] Update API client with priority and tags in frontend/src/services/api.ts

**Acceptance Test**: Create tasks with various priorities and tags → sort by priority → filter by tag → verify correct results

---

## Phase 6: User Story 4 - Search & Filter (P2) (5-8 hours)

**User Story**: A user needs to quickly find tasks using full-text search and apply multiple filters.

**Independent Test**: Create diverse tasks, verify search returns relevant results, filters narrow correctly.

**Value**: Productivity for large task lists, quick task location.

### Backend Tasks

- [ ] T077 [P] [US4] Create SearchService with PostgreSQL FTS in backend/app/services/search_service.py
- [ ] T078 [US4] Add GIN index for full-text search in Alembic migration 008_add_search_indexes.py
- [ ] T079 [US4] Run migration to add search indexes
- [ ] T080 [US4] Implement GET /api/v2/todos/search endpoint in backend/app/api/v2/search.py
- [ ] T081 [US4] Implement multi-criteria filter logic in backend/app/services/todo_service.py
- [ ] T082 [US4] Update GET /api/v2/todos with filter parameters in backend/app/api/v2/todos.py
- [ ] T083 [US4] Add sort parameter support (created_at, due_date, priority, title) in backend/app/api/v2/todos.py

### Frontend Tasks

- [ ] T084 [P] [US4] Create SearchBar component in frontend/src/components/todos/SearchBar.tsx
- [ ] T085 [P] [US4] Create FilterPanel component in frontend/src/components/todos/FilterPanel.tsx
- [ ] T086 [US4] Add search and filter to TodoList in frontend/src/components/todos/TodoList.tsx
- [ ] T087 [US4] Create useSearch hook in frontend/src/hooks/useSearch.ts
- [ ] T088 [US4] Update API client with search and filter in frontend/src/services/api.ts

**Acceptance Test**: Create 20+ diverse tasks → search for keyword → apply multiple filters → verify correct results in <1 second

---

## Phase 7: User Story 5 - Real-Time Sync (P2) (7-10 hours)

**User Story**: A user working across multiple devices needs to see task updates instantly without manual refresh.

**Independent Test**: Open app in two browser tabs, create task in one, verify appears in other within 2 seconds.

**Value**: Modern UX expectation, prevents conflicts across devices.

### Backend Tasks

- [ ] T089 [P] [US5] Create EventPublisher service with Dapr pub/sub in backend/app/services/event_publisher.py
- [ ] T090 [US5] Integrate EventPublisher in TodoService for all CRUD operations in backend/app/services/todo_service.py
- [ ] T091 [US5] Publish task-updates events on create/update/delete in backend/app/services/todo_service.py
- [ ] T092 [US5] Add event schemas validation in backend/app/services/event_publisher.py

### Microservice Tasks

- [ ] T093 [P] [US5] Create websocket-service structure in services/websocket-service/
- [ ] T094 [P] [US5] Implement ConnectionManager in services/websocket-service/app/connection_manager.py
- [ ] T095 [US5] Implement Dapr subscriber for task-updates in services/websocket-service/app/dapr_subscriber.py
- [ ] T096 [US5] Implement WebSocket server in services/websocket-service/app/main.py
- [ ] T097 [US5] Create Dockerfile for websocket-service in services/websocket-service/

### Frontend Tasks

- [ ] T098 [P] [US5] Create WebSocket client in frontend/src/services/websocket.ts
- [ ] T099 [P] [US5] Create RealtimeSync component in frontend/src/components/realtime/RealtimeSync.tsx
- [ ] T100 [US5] Create useRealtime hook in frontend/src/hooks/useRealtime.ts
- [ ] T101 [US5] Integrate RealtimeSync in TodoList in frontend/src/components/todos/TodoList.tsx
- [ ] T102 [US5] Add offline queue and sync logic in frontend/src/services/websocket.ts

### Deployment Tasks

- [ ] T103 [US5] Add websocket-service to Helm chart in helm/todo-chatbot/templates/websocket-service/
- [ ] T104 [US5] Update Helm values with websocket-service config in helm/todo-chatbot/values.yaml
- [ ] T105 [US5] Deploy to Minikube and test real-time sync across two browser tabs

**Acceptance Test**: Open two browser tabs → create task in tab 1 → verify appears in tab 2 within 2 seconds

---

## Phase 8: User Story 6 - Audit Trail (P3) (4-6 hours)

**User Story**: A user or administrator needs to view history of all task operations for accountability.

**Independent Test**: Perform various task operations, verify all logged with timestamps and user info.

**Value**: Transparency and accountability, compliance requirements.

### Backend Tasks

- [ ] T106 [P] [US6] Create AuditEvent model in backend/app/models/audit_event.py
- [ ] T107 [US6] Create Alembic migration 009_add_audit_events.py in backend/migrations/versions/
- [ ] T108 [US6] Run migration to create audit_events table
- [ ] T109 [US6] Create AuditService in backend/app/services/audit_service.py
- [ ] T110 [US6] Implement GET /api/v2/audit endpoint in backend/app/api/v2/audit.py
- [ ] T111 [US6] Implement GET /api/v2/todos/{id}/history endpoint in backend/app/api/v2/todos.py

### Microservice Tasks

- [ ] T112 [P] [US6] Create audit-service structure in services/audit-service/
- [ ] T113 [P] [US6] Implement storage logic in services/audit-service/app/storage.py
- [ ] T114 [US6] Implement Dapr subscriber for task-events in services/audit-service/app/dapr_subscriber.py
- [ ] T115 [US6] Implement main service logic in services/audit-service/app/main.py
- [ ] T116 [US6] Create Dockerfile for audit-service in services/audit-service/

### Deployment Tasks

- [ ] T117 [US6] Add audit-service to Helm chart in helm/todo-chatbot/templates/audit-service/
- [ ] T118 [US6] Update Helm values with audit-service config in helm/todo-chatbot/values.yaml
- [ ] T119 [US6] Deploy to Minikube and test audit trail recording

**Acceptance Test**: Create/update/delete tasks → query audit trail → verify all operations logged with 100% accuracy

---

## Phase 9: User Story 7 - Automated Deployment (P3) (5-8 hours)

**User Story**: Development team needs automated building, testing, and deployment with minimal manual intervention.

**Independent Test**: Push code changes, verify CI/CD pipeline builds, tests, and deploys automatically.

**Value**: Development velocity, reduced deployment errors.

### Cloud Infrastructure Tasks

- [ ] T120 Create DOKS cluster on DigitalOcean (smallest size)
- [ ] T121 Get kubeconfig and configure kubectl for DOKS
- [ ] T122 Install Dapr on DOKS cluster (dapr init -k)
- [ ] T123 Update Dapr components for production (Redpanda Cloud URLs) in k8s/dapr-components/
- [ ] T124 Install cert-manager on DOKS for TLS certificates
- [ ] T125 Install NGINX Ingress Controller on DOKS
- [ ] T126 Create Ingress resource with TLS in k8s/base/frontend/ingress.yaml

### CI/CD Pipeline Tasks

- [ ] T127 [P] Create GitHub Actions workflow: ci.yml in .github/workflows/
- [ ] T128 [P] Create GitHub Actions workflow: deploy-production.yml in .github/workflows/
- [ ] T129 Add Docker build and push steps for all services in .github/workflows/ci.yml
- [ ] T130 Add Trivy security scanning in .github/workflows/ci.yml
- [ ] T131 Add Helm upgrade step with DOKS kubeconfig in .github/workflows/deploy-production.yml
- [ ] T132 Configure GitHub secrets for Docker Hub and DOKS credentials
- [ ] T133 Test CI/CD pipeline with dummy commit

**Acceptance Test**: Push code change → verify pipeline builds, scans, and deploys → verify app accessible with TLS

---

## Phase 10: Polish & Cross-Cutting Concerns (3-5 hours)

**Goal**: Add observability, documentation, and final polish for production readiness.

**Deliverables**: Grafana dashboards, architecture documentation, troubleshooting guide, demo video.

### Observability Tasks

- [ ] T134 [P] Create Prometheus metrics endpoints in all services
- [ ] T135 [P] Create Grafana dashboard for backend metrics in monitoring/grafana/dashboards/backend.json
- [ ] T136 [P] Create Grafana dashboard for microservices in monitoring/grafana/dashboards/microservices.json
- [ ] T137 Deploy Prometheus and Grafana to DOKS cluster

### Documentation Tasks

- [ ] T138 [P] Create architecture diagram in docs/architecture.md
- [ ] T139 [P] Create event flow documentation in docs/event-flows.md
- [ ] T140 [P] Create deployment guide in docs/deployment.md
- [ ] T141 [P] Create troubleshooting guide in docs/troubleshooting.md
- [ ] T142 Update main README.md with Phase V deployment instructions and public URL
- [ ] T143 Record 60-90 second demo video showing all features
- [ ] T144 Create quickstart guide in specs/001-phase5-cloud-deployment/quickstart.md

**Final Acceptance**: All 12 success criteria from spec.md verified, system running in production with TLS

---

## Dependencies & Execution Order

### Critical Path
1. **Phase 1** (Setup) → **Phase 2** (Foundational) → **Phase 3** (US1) → MVP Complete
2. After MVP, user stories can be implemented in any order (P1 → P2 → P3 recommended)
3. **Phase 9** (Deployment) can start after any user story is complete
4. **Phase 10** (Polish) should be last

### User Story Dependencies
- **US1-US6**: Independent, can be implemented in parallel after Phase 2
- **US7**: Depends on at least one user story being complete for deployment testing
- **Phase 10**: Depends on all user stories being complete

### Parallel Execution Examples

**Phase 3 (US1) Parallel Opportunities**:
- T021, T022 (models) can run in parallel
- T030, T031 (microservice) can run in parallel with T035, T036 (frontend)
- T040, T041 (chatbot) can run in parallel with other tasks

**Phase 4 (US2) Parallel Opportunities**:
- T045, T046 (models) can run in parallel
- T053, T054, T055 (microservice) can run in parallel with T059, T060 (frontend)

**Phase 10 (Polish) Parallel Opportunities**:
- T134, T135, T136 (observability) can all run in parallel
- T138, T139, T140, T141 (documentation) can all run in parallel

---

## Success Criteria Validation

After completing all tasks, verify these success criteria from spec.md:

### Functional Requirements
- [ ] All advanced todo features work via UI and chatbot
- [ ] Recurring tasks automatically create next instance on completion
- [ ] Reminders are triggered at scheduled times
- [ ] Real-time updates appear across multiple devices within 2 seconds
- [ ] Full-text search returns results in under 1 second
- [ ] Filter and sort work with multiple criteria
- [ ] Audit trail records all operations with 100% accuracy

### Non-Functional Requirements
- [ ] System handles 1,000 concurrent users without degradation
- [ ] API response time under 200ms for 95% of requests
- [ ] Event processing latency under 100ms for 99% of events
- [ ] Zero-downtime deployments with automatic rollback
- [ ] TLS certificates automatically renewed
- [ ] 99.9% uptime over 30-day period

### Deployment Requirements
- [ ] Full stack runs on Minikube with Dapr + Redpanda Docker
- [ ] Application deployed and accessible on DOKS with TLS
- [ ] CI/CD pipeline successfully builds and deploys
- [ ] Prometheus/Grafana dashboards show health metrics

---

## Notes

- **MVP First**: Implement Phase 1-3 for MVP (recurring tasks), then iterate
- **Independent Stories**: Each user story (Phase 3-8) can be tested independently
- **Parallel Development**: Multiple developers can work on different user stories simultaneously
- **Incremental Value**: Each completed user story delivers immediate value to users
- **Task Format**: All tasks follow strict checklist format with IDs, labels, and file paths
- **Estimated Effort**: 35-60 hours total, 4-6 weeks part-time development

---

**Generated by**: Claude Opus 4.6
**Date**: 2026-02-10
**Status**: Ready for implementation
