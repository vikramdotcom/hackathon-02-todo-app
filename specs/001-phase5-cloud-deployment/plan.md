# Implementation Plan: Phase V - Cloud-Native Event-Driven Todo System

**Branch**: `001-phase5-cloud-deployment` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase5-cloud-deployment/spec.md`

## Summary

Transform the Todo Chatbot application from a basic cloud-native deployment (Phase IV – Minikube) into a production-grade, event-driven, decoupled microservices system. This phase adds advanced todo features (recurring tasks, due dates, reminders, priorities, tags, search/filter), implements event-driven architecture with Kafka/Redpanda, uses Dapr for service abstraction, deploys to managed Kubernetes (DOKS), and establishes automated CI/CD pipeline with production-grade observability and TLS.

**Core Principle**: Extend existing application without redesigning core logic. Add new features and refactor communication to become event-driven and loosely coupled.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Node.js 18+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy, Dapr SDK, Kafka client
- Frontend: Next.js 14, React 18, TailwindCSS
- Infrastructure: Dapr, Redpanda Cloud, Neon PostgreSQL, DOKS

**Storage**:
- Primary: Neon PostgreSQL (serverless, managed)
- State: Dapr state store (PostgreSQL-backed)
- Events: Redpanda Cloud (Kafka-compatible)

**Testing**:
- Backend: pytest, pytest-asyncio
- Frontend: Jest, React Testing Library
- Integration: Kubernetes test pods, Helm test hooks

**Target Platform**:
- Local: Minikube with Dapr
- Production: DigitalOcean Kubernetes (DOKS)

**Project Type**: Web application (frontend + backend + microservices)

**Performance Goals**:
- API response time: <200ms p95
- Event processing latency: <100ms p99
- Real-time update latency: <2 seconds
- Search response time: <1 second for 10k items
- Support 1,000 concurrent users

**Constraints**:
- Zero-downtime deployments required
- TLS encryption for all external traffic
- 99.9% uptime SLA
- Event ordering must be maintained per task
- Audit trail must be 100% accurate

**Scale/Scope**:
- 10,000 concurrent users
- 10,000 events per minute peak
- 10,000 items per user task list
- 4 new microservices (recurring, notification, websocket, audit)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development (SDD)
- **Status**: PASS
- **Evidence**: Comprehensive specification created with 32 functional requirements, 12 success criteria, and 7 prioritized user stories
- **Action**: All implementation will be generated from specifications

### ✅ Strict Data Model Compliance
- **Status**: PASS with EXTENSION
- **Evidence**: Existing Todo schema preserved; new fields added as extensions (due_date, priority, tags, recurrence, reminder_offsets)
- **Justification**: Extensions are additive and backward-compatible; existing Phase I-IV functionality remains intact
- **Action**: Document schema extensions in data-model.md

### ✅ Phase Isolation & Forward Compatibility
- **Status**: PASS
- **Evidence**: Phase V extends Phase IV without breaking existing deployments; all APIs remain backward-compatible
- **Action**: Ensure API versioning and graceful degradation when new features unavailable

### ✅ Feature Completeness
- **Status**: PASS
- **Evidence**: All requirements have clear intent, defined inputs/outputs, explicit constraints, and acceptance criteria
- **Action**: Maintain requirement traceability through implementation

### ✅ Code Generation & Validation
- **Status**: PASS
- **Evidence**: Claude Code will generate all implementations; validation against specification required
- **Action**: Create comprehensive test suite based on acceptance criteria

## Project Structure

### Documentation (this feature)

```text
specs/001-phase5-cloud-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - technology decisions and patterns
├── data-model.md        # Phase 1 output - extended Todo schema
├── quickstart.md        # Phase 1 output - setup and deployment guide
├── contracts/           # Phase 1 output - API contracts and event schemas
│   ├── api/
│   │   ├── todos-v2.openapi.yaml
│   │   ├── search.openapi.yaml
│   │   └── audit.openapi.yaml
│   └── events/
│       ├── task-events.avsc
│       ├── reminders.avsc
│       └── task-updates.avsc
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phase-5-cloud-deployment/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── todo.py              # Extended with new fields
│   │   │   ├── recurrence.py        # New: recurrence patterns
│   │   │   ├── reminder.py          # New: reminder scheduling
│   │   │   └── audit_event.py       # New: audit trail
│   │   ├── api/
│   │   │   ├── v2/                  # New API version
│   │   │   │   ├── todos.py         # Extended CRUD with new features
│   │   │   │   ├── search.py        # New: full-text search
│   │   │   │   └── audit.py         # New: audit trail queries
│   │   │   └── v1/                  # Existing API (backward compat)
│   │   ├── services/
│   │   │   ├── todo_service.py      # Extended with new operations
│   │   │   ├── search_service.py    # New: search and filter
│   │   │   ├── event_publisher.py   # New: Dapr pub/sub
│   │   │   └── audit_service.py     # New: audit logging
│   │   └── dapr/
│   │       └── client.py            # Dapr SDK wrapper
│   ├── migrations/
│   │   └── versions/
│   │       └── 005_add_advanced_features.py
│   └── Dockerfile
│
├── services/
│   ├── recurring-task-service/
│   │   ├── app/
│   │   │   ├── main.py              # Event consumer for recurring tasks
│   │   │   ├── recurrence_engine.py # Calculate next occurrence
│   │   │   └── dapr_subscriber.py   # Dapr pub/sub subscription
│   │   └── Dockerfile
│   │
│   ├── notification-service/
│   │   ├── app/
│   │   │   ├── main.py              # Reminder processor
│   │   │   ├── scheduler.py         # Cron-based reminder checker
│   │   │   ├── notifier.py          # Send notifications
│   │   │   └── dapr_subscriber.py   # Dapr pub/sub + cron binding
│   │   └── Dockerfile
│   │
│   ├── websocket-service/
│   │   ├── app/
│   │   │   ├── main.py              # WebSocket server
│   │   │   ├── connection_manager.py # Manage client connections
│   │   │   └── dapr_subscriber.py   # Subscribe to task-updates
│   │   └── Dockerfile
│   │
│   └── audit-service/
│       ├── app/
│       │   ├── main.py              # Audit event processor
│       │   ├── storage.py           # Persist audit events
│       │   └── dapr_subscriber.py   # Subscribe to task-events
│       └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── todos/
│   │   │   │   ├── TodoForm.tsx     # Extended with new fields
│   │   │   │   ├── TodoList.tsx     # Enhanced with filters/sort
│   │   │   │   ├── SearchBar.tsx    # New: search interface
│   │   │   │   ├── FilterPanel.tsx  # New: filter controls
│   │   │   │   └── RecurrenceSelector.tsx # New: recurrence UI
│   │   │   └── realtime/
│   │   │       └── RealtimeSync.tsx # New: WebSocket client
│   │   ├── hooks/
│   │   │   ├── useTodos.ts          # Extended with new features
│   │   │   ├── useSearch.ts         # New: search hook
│   │   │   └── useRealtime.ts       # New: WebSocket hook
│   │   └── services/
│   │       ├── api.ts               # Extended API client
│   │       └── websocket.ts         # New: WebSocket client
│   └── Dockerfile
│
├── k8s/
│   ├── dapr-components/
│   │   ├── kafka-pubsub.yaml        # Redpanda pub/sub component
│   │   ├── statestore.yaml          # PostgreSQL state store
│   │   ├── reminder-cron.yaml       # Cron binding for reminders
│   │   └── k8s-secrets.yaml         # Kubernetes secret store
│   │
│   ├── base/
│   │   ├── backend/
│   │   │   ├── deployment.yaml      # With Dapr annotations
│   │   │   ├── service.yaml
│   │   │   └── configmap.yaml
│   │   ├── frontend/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── ingress.yaml         # With TLS
│   │   ├── recurring-service/
│   │   │   ├── deployment.yaml      # With Dapr annotations
│   │   │   └── service.yaml
│   │   ├── notification-service/
│   │   │   ├── deployment.yaml      # With Dapr annotations
│   │   │   └── service.yaml
│   │   ├── websocket-service/
│   │   │   ├── deployment.yaml      # With Dapr annotations
│   │   │   └── service.yaml
│   │   └── audit-service/
│   │       ├── deployment.yaml      # With Dapr annotations
│   │       └── service.yaml
│   │
│   └── overlays/
│       ├── local/                   # Minikube configuration
│       │   └── kustomization.yaml
│       └── production/              # DOKS configuration
│           └── kustomization.yaml
│
├── helm/
│   └── todo-chatbot/
│       ├── Chart.yaml               # Extended from Phase IV
│       ├── values.yaml              # New services + Dapr config
│       ├── values-local.yaml        # Minikube values
│       ├── values-prod.yaml         # DOKS values
│       └── templates/
│           ├── backend/
│           ├── frontend/
│           ├── recurring-service/   # New
│           ├── notification-service/ # New
│           ├── websocket-service/   # New
│           ├── audit-service/       # New
│           └── dapr-components/     # New
│
├── .github/
│   └── workflows/
│       ├── ci.yml                   # Build and test
│       ├── deploy-staging.yml       # Deploy to staging
│       └── deploy-production.yml    # Deploy to production
│
├── scripts/
│   ├── setup-local.sh               # Setup Minikube + Dapr
│   ├── setup-redpanda.sh            # Configure Redpanda topics
│   ├── deploy-local.sh              # Deploy to Minikube
│   ├── deploy-doks.sh               # Deploy to DOKS
│   └── test-e2e.sh                  # End-to-end tests
│
└── docs/
    ├── architecture.md              # System architecture diagram
    ├── event-flows.md               # Event-driven flows
    ├── deployment.md                # Deployment guide
    └── troubleshooting.md           # Common issues
```

**Structure Decision**: Web application with microservices architecture. Backend extended with new features, 4 new microservices for event-driven operations, frontend enhanced with new UI components. Kubernetes manifests organized with Kustomize overlays for local/production environments. Helm charts extended from Phase IV with new services and Dapr components.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Schema Extension | Add advanced todo features (recurring, reminders, priorities, tags) | Cannot deliver Phase V requirements without extending schema; extensions are additive and backward-compatible |
| 4 New Microservices | Event-driven architecture requires decoupled services for recurring tasks, notifications, real-time sync, and audit | Monolithic approach would violate loose coupling principle and prevent independent scaling |
| Event-Driven Architecture | Real-time synchronization and audit trail require event streaming | Direct API calls cannot provide real-time updates across devices or reliable audit trail |

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **Redpanda Cloud Setup and Configuration**
   - Research: Redpanda Cloud serverless tier capabilities and limitations
   - Decision: Use Redpanda Cloud for Kafka-compatible event streaming
   - Rationale: Free tier available, fully managed, Kafka-compatible, lower latency than Kafka
   - Alternatives: Confluent Cloud (more expensive), self-hosted Kafka (operational overhead)

2. **Dapr Building Blocks Selection**
   - Research: Dapr pub/sub, state management, service invocation, bindings, secrets
   - Decision: Use all 5 building blocks for complete abstraction
   - Rationale: Simplifies microservices development, portable across clouds, built-in resilience
   - Alternatives: Direct Kafka/Redis clients (more code, less portable)

3. **Recurring Task Implementation Pattern**
   - Research: Cron-based vs event-driven recurring task generation
   - Decision: Event-driven with completion trigger + cron fallback
   - Rationale: Immediate next instance on completion, cron catches missed instances
   - Alternatives: Pure cron (delayed regeneration), pure event (no recovery from failures)

4. **Real-Time Synchronization Approach**
   - Research: WebSocket vs Server-Sent Events (SSE) vs polling
   - Decision: WebSocket with Dapr pub/sub backend
   - Rationale: Bidirectional, low latency, Dapr handles event distribution
   - Alternatives: SSE (unidirectional), polling (high latency, inefficient)

5. **Search Implementation Strategy**
   - Research: PostgreSQL full-text search vs Elasticsearch vs Algolia
   - Decision: PostgreSQL full-text search with GIN indexes
   - Rationale: No additional infrastructure, sufficient for 10k items, already using PostgreSQL
   - Alternatives: Elasticsearch (operational overhead), Algolia (cost)

6. **Database Schema Migration Strategy**
   - Research: Alembic vs raw SQL vs SQLAlchemy-migrate
   - Decision: Alembic with backward-compatible migrations
   - Rationale: Industry standard, supports rollback, integrates with SQLAlchemy
   - Alternatives: Raw SQL (error-prone), SQLAlchemy-migrate (deprecated)

7. **CI/CD Pipeline Design**
   - Research: GitHub Actions vs GitLab CI vs Jenkins
   - Decision: GitHub Actions with Helm deployment
   - Rationale: Native GitHub integration, free for public repos, simple YAML config
   - Alternatives: GitLab CI (requires GitLab), Jenkins (self-hosted complexity)

8. **TLS Certificate Management**
   - Research: cert-manager vs manual Let's Encrypt vs cloud provider certs
   - Decision: cert-manager with Let's Encrypt
   - Rationale: Automatic renewal, Kubernetes-native, free certificates
   - Alternatives: Manual (operational burden), cloud certs (vendor lock-in)

### Technology Stack Summary

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Event Streaming | Redpanda Cloud | Kafka-compatible, serverless, free tier, low latency |
| Service Runtime | Dapr | Portable abstractions, built-in resilience, simplifies microservices |
| Database | Neon PostgreSQL | Serverless, scale-to-zero, generous free tier, managed |
| Kubernetes | DOKS | Managed, affordable, simple setup, good documentation |
| CI/CD | GitHub Actions | Native integration, free, simple configuration |
| TLS | cert-manager + Let's Encrypt | Automatic renewal, free, Kubernetes-native |
| Search | PostgreSQL FTS | No additional infrastructure, sufficient performance |
| Real-time | WebSocket + Dapr | Low latency, bidirectional, event-driven backend |

## Phase 1: Design & Contracts

### Data Model Extensions

See [data-model.md](./data-model.md) for complete schema definitions.

**Extended Todo Entity**:
- Existing fields: id, title, description, completed, created_at, updated_at, user_id
- New fields: due_date, priority, tags, recurrence_pattern, reminder_offsets

**New Entities**:
- RecurrencePattern: frequency, interval, end_condition, next_occurrence
- Reminder: todo_id, offset_minutes, status, scheduled_time
- AuditEvent: event_type, timestamp, user_id, todo_id, changes

### API Contracts

See [contracts/api/](./contracts/api/) for complete OpenAPI specifications.

**Extended Endpoints**:
- `POST /api/v2/todos` - Create todo with advanced features
- `GET /api/v2/todos` - List with search, filter, sort
- `GET /api/v2/todos/search` - Full-text search
- `GET /api/v2/audit` - Query audit trail

**New Endpoints**:
- `GET /api/v2/todos/{id}/history` - Todo change history
- `POST /api/v2/todos/{id}/snooze` - Snooze reminder
- `GET /api/v2/reminders/upcoming` - Upcoming reminders

### Event Schemas

See [contracts/events/](./contracts/events/) for complete Avro schemas.

**Event Topics**:
1. `task-events` - All CRUD operations (created, updated, completed, deleted)
2. `reminders` - Reminder scheduling and triggering
3. `task-updates` - Real-time UI updates

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DOKS Cluster                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Frontend   │  │   Backend    │  │  WebSocket   │        │
│  │   (Next.js)  │  │  (FastAPI)   │  │   Service    │        │
│  │              │  │              │  │              │        │
│  │  Dapr: N/A   │  │ Dapr: Pub/Sub│  │ Dapr: Pub/Sub│        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│         │                  │                  │                │
│         │                  │                  │                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Recurring   │  │ Notification │  │    Audit     │        │
│  │   Service    │  │   Service    │  │   Service    │        │
│  │              │  │              │  │              │        │
│  │ Dapr: Pub/Sub│  │Dapr: Pub/Sub │  │ Dapr: Pub/Sub│        │
│  │       State  │  │      Cron    │  │       State  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Dapr Control Plane                         │  │
│  │  (Sidecar Injector, Operator, Placement Service)       │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌─────────▼────────┐  ┌────────▼────────┐
│ Redpanda Cloud │  │ Neon PostgreSQL  │  │ cert-manager    │
│ (Event Stream) │  │ (Database)       │  │ (TLS Certs)     │
└────────────────┘  └──────────────────┘  └─────────────────┘
```

## Phase 2: Implementation Stages

### Stage 0: Preparation (1-2 hours)

**Tasks**:
1. Create `/phase-5-cloud-deployment` folder structure
2. Copy Phase IV Helm charts as starting point
3. Update main README with Phase V section
4. Setup local development environment

**Deliverables**:
- Project structure created
- Helm charts copied and ready for extension
- README updated

### Stage 1: Advanced Todo Features (6-12 hours)

**Backend Tasks**:
1. Extend Todo model with new fields
2. Create Alembic migration for schema changes
3. Update CRUD endpoints to accept new fields
4. Implement search endpoint with PostgreSQL FTS
5. Implement filter and sort logic
6. Add validation for new fields

**Frontend Tasks**:
1. Extend TodoForm with new input fields
2. Create RecurrenceSelector component
3. Create FilterPanel component
4. Create SearchBar component
5. Update TodoList with filter/sort controls
6. Add visual indicators for priority and due dates

**Chatbot Tasks**:
1. Update LLM prompts to understand new commands
2. Extend function schemas for new fields
3. Add natural language date parsing
4. Test chatbot with new features

**Checkpoint**: All new features work via UI and chatbot (direct API calls, no events yet)

### Stage 2: Redpanda Cloud Setup (1-2 hours)

**Tasks**:
1. Sign up for Redpanda Cloud serverless tier
2. Create cluster and topics (task-events, reminders, task-updates)
3. Configure SASL authentication
4. Test connection with Python producer/consumer
5. Document connection details in secrets

**Deliverables**:
- Redpanda cluster provisioned
- Topics created
- Connection tested
- Credentials stored securely

### Stage 3: Dapr Integration (4-8 hours)

**Tasks**:
1. Install Dapr CLI locally
2. Initialize Dapr in Minikube (`dapr init -k`)
3. Create Dapr component YAMLs:
   - kafka-pubsub.yaml (Redpanda connection)
   - statestore.yaml (PostgreSQL state)
   - reminder-cron.yaml (cron binding)
   - k8s-secrets.yaml (secret store)
4. Apply components to Minikube
5. Verify components with `dapr dashboard`

**Deliverables**:
- Dapr installed and running
- All components configured
- Components verified healthy

### Stage 4: Event-Driven Refactoring (8-15 hours)

**Backend Refactoring**:
1. Add Dapr SDK to dependencies
2. Create event publisher service
3. Publish events on all CRUD operations
4. Replace direct Kafka client with Dapr pub/sub
5. Add event schemas and validation

**New Microservices**:

1. **Recurring Task Service**:
   - Subscribe to task-events topic
   - Detect completed recurring tasks
   - Calculate next occurrence
   - Create new task instance
   - Use Dapr state for tracking

2. **Notification Service**:
   - Subscribe to reminders topic
   - Implement cron binding for periodic checks
   - Query upcoming reminders
   - Send notifications (log/email simulation)
   - Mark reminders as sent

3. **WebSocket Service**:
   - Subscribe to task-updates topic
   - Manage WebSocket connections
   - Broadcast updates to connected clients
   - Handle connection lifecycle

4. **Audit Service**:
   - Subscribe to task-events topic
   - Store all events in audit table
   - Provide query API for audit trail
   - Implement retention policy

**Checkpoint**: Events flow through system, services log events correctly

### Stage 5: Local Deployment (3-6 hours)

**Tasks**:
1. Extend Helm chart with new services
2. Add Dapr annotations to all deployments
3. Configure Dapr components in Helm
4. Deploy to Minikube with Helm
5. Test full event-driven flow
6. Verify real-time updates work

**Test Scenarios**:
- Create recurring task → complete → verify next instance created
- Set due date + reminder → verify reminder triggered
- Open two browsers → verify real-time sync
- Perform operations → verify audit trail

**Deliverables**:
- Helm chart extended
- All services deployed to Minikube
- End-to-end tests passing

### Stage 6: Cloud Deployment (4-8 hours)

**Tasks**:
1. Create DOKS cluster (smallest size)
2. Get kubeconfig and configure kubectl
3. Install Dapr on DOKS (`dapr init -k`)
4. Update Dapr components for production (Redpanda Cloud URLs)
5. Deploy Helm chart to DOKS
6. Install cert-manager and NGINX Ingress
7. Configure Ingress with TLS
8. Test public access

**Deliverables**:
- DOKS cluster provisioned
- Application deployed to cloud
- TLS configured and working
- Public URL accessible

### Stage 7: CI/CD Pipeline (3-5 hours)

**Tasks**:
1. Create GitHub Actions workflow
2. Configure Docker Hub credentials
3. Add build and push steps for all services
4. Add Trivy security scanning
5. Add Helm upgrade step with DOKS kubeconfig
6. Test pipeline with dummy commit

**Deliverables**:
- CI/CD pipeline configured
- Automated deployments working
- Security scanning enabled

### Stage 8: Polish & Documentation (2-4 hours)

**Tasks**:
1. Add Grafana dashboards for services
2. Create architecture diagram
3. Write deployment documentation
4. Create troubleshooting guide
5. Record demo video
6. Update main README

**Deliverables**:
- Documentation complete
- Demo video recorded
- README updated with Phase V info

## Acceptance Criteria

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

## Risk Mitigation

### Technical Risks

1. **Event streaming outage**: Implement event queuing and retry logic; use managed service with HA SLA
2. **Database performance**: Add indexes on frequently queried fields; use pagination; consider read replicas
3. **Real-time sync conflicts**: Implement last-write-wins with user notification; add optimistic locking
4. **Reminder delivery failures**: Implement retry logic; provide in-app fallback; log all attempts
5. **Recurring task errors**: Comprehensive unit tests; idempotency checks; manual recovery tools

### Operational Risks

1. **Infrastructure costs**: Monitor closely; use serverless/scale-to-zero; set cost alerts
2. **Deployment failures**: Automated rollback; blue-green deployments; maintain backups
3. **Insufficient monitoring**: Comprehensive health checks; alerting; on-call procedures

## Next Steps

1. **Phase 0 Complete**: Review research.md and validate technology decisions
2. **Phase 1 Complete**: Review data-model.md and contracts/ for API/event schemas
3. **Ready for Tasks**: Run `/sp.tasks` to generate actionable implementation tasks
4. **Implementation**: Execute tasks in dependency order, starting with Stage 0

---

**Plan Status**: Complete and ready for task generation
**Estimated Effort**: 35-60 hours total implementation time
**Target Completion**: 4-6 weeks with part-time development
