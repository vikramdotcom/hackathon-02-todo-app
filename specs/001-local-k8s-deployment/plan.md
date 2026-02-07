# Implementation Plan: Local Kubernetes Deployment

**Branch**: `001-local-k8s-deployment` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-local-k8s-deployment/spec.md`

## Summary

Deploy the Phase III AI-Powered Todo Chatbot application to a local Kubernetes cluster (Minikube) using containerization (Docker), orchestration (Kubernetes), and package management (Helm). The deployment must be fully automated via AI-generated artifacts, require no manual YAML/Dockerfile writing, and maintain 100% Phase III application functionality without any business logic changes. The system will support one-command deployment, environment reproducibility across Windows/macOS/Linux, independent service scaling, and comprehensive troubleshooting capabilities.

## Technical Context

**Language/Version**:
- Frontend: Node.js 18+, Next.js 14.0.0, TypeScript 5.3.0
- Backend: Python 3.11+, FastAPI 0.104.0+

**Primary Dependencies**:
- Frontend: React 18.2.0, Tailwind CSS 3.3.6, Axios 1.6.0
- Backend: SQLModel 0.0.14, Alembic 1.12.0, OpenAI 1.12.0, Uvicorn, Python-Jose, Passlib
- Infrastructure: Docker 24.0+, Minikube 1.30+, kubectl 1.28+, Helm 3.12+

**Storage**:
- Database: PostgreSQL (production) or SQLite (development)
- Session Storage: In-memory (current), Redis (optional for distributed deployment)
- Persistent Volumes: Required for database data persistence across pod restarts

**Testing**:
- Backend: pytest with async support, unit/integration/e2e test structure
- Frontend: Jest/React Testing Library (standard Next.js setup)
- Infrastructure: Helm chart validation, Kubernetes manifest linting

**Target Platform**:
- Local Development: Minikube on Windows 10+, macOS 11+, Ubuntu 20.04+
- Kubernetes Version: 1.28+ (Minikube default)
- Container Runtime: Docker (Minikube driver)

**Project Type**: Web application (frontend + backend microservices)

**Performance Goals**:
- Deployment time: <10 minutes from clean environment
- Service startup: All services ready within 5 minutes
- Health check response: <10 seconds to detect failures
- Scaling operations: <1 minute to add/remove replicas

**Constraints**:
- No application logic changes (Phase III code remains unchanged)
- All infrastructure artifacts generated via AI tools (no manual YAML/Dockerfile writing)
- Resource limits: 8GB RAM minimum, 20GB disk space for Minikube
- Cross-platform compatibility: Windows, macOS, Linux
- Zero data loss during service restarts

**Scale/Scope**:
- Services: 3 containerized services (frontend, backend, database)
- Replicas: 1-3 per service (configurable via Helm)
- Concurrent deployments: Support 10+ on same network without conflicts
- Configuration profiles: Development, testing (production in Phase V)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Spec-Driven Development (SDD)
**Status**: PASS
- All infrastructure artifacts will be generated from specifications
- Docker AI (Gordon), kubectl-ai, and Claude Code will generate Dockerfiles, Kubernetes manifests, and Helm charts
- No manual YAML or Dockerfile writing permitted
- If artifacts are incorrect, specifications will be refined, not code manually edited

### ✅ II. Strict Data Model Compliance
**Status**: PASS
- Phase III database schema remains unchanged (Users table, Todos table)
- No modifications to canonical Todo schema (id, title, description, completion metadata)
- Alembic migration 001 will be reused without changes
- Database persistence via Kubernetes PersistentVolumes maintains schema integrity

### ✅ III. Phase Isolation & Forward Compatibility
**Status**: PASS
- Phase IV is architecturally independent (containerization layer only)
- Phase III application code copied to `/phase-4-kubernetes/` directory for isolation
- No changes to Phase III APIs or contracts
- Kubernetes manifests designed for Phase V cloud migration (reusable Helm charts)
- All configuration externalized via ConfigMaps/Secrets for environment flexibility

### ✅ IV. Feature Completeness
**Status**: PASS
- Clear intent: Enable local Kubernetes deployment for development/testing
- Defined inputs: Phase III application code, Docker/Minikube/kubectl/Helm prerequisites
- Defined outputs: Running Kubernetes cluster with all services accessible
- Explicit constraints: 8GB RAM, no application changes, AI-generated artifacts only
- Acceptance criteria: 20 functional requirements, 15 success criteria (all testable)

### ✅ V. Code Generation & Validation
**Status**: PASS
- Claude Code is the sole authority for infrastructure code generation
- All Dockerfiles generated via Docker AI (Gordon) or Claude Code
- All Kubernetes manifests generated via kubectl-ai or Claude Code
- Helm charts generated via Claude Code following best practices
- Validation via deployment testing, health checks, and functional verification

### Constitution Compliance Summary
**All gates passed.** No violations. Phase IV is fully compliant with constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-local-k8s-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output: Technology decisions and best practices
├── data-model.md        # Phase 1 output: Deployment configuration entities
├── quickstart.md        # Phase 1 output: Getting started guide
├── contracts/           # Phase 1 output: Kubernetes resource contracts
│   ├── deployment-contract.yaml    # Deployment resource specification
│   ├── service-contract.yaml       # Service resource specification
│   ├── configmap-contract.yaml     # ConfigMap resource specification
│   ├── secret-contract.yaml        # Secret resource specification
│   └── helm-values-schema.yaml     # Helm values.yaml schema
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phase-4-kubernetes/                    # Phase IV isolated directory
├── docker/                            # Docker containerization artifacts
│   ├── frontend/
│   │   ├── Dockerfile                # AI-generated Next.js Dockerfile
│   │   ├── .dockerignore            # Exclude node_modules, .next, etc.
│   │   └── nginx.conf               # Optional: NGINX for production serving
│   ├── backend/
│   │   ├── Dockerfile                # AI-generated FastAPI Dockerfile
│   │   ├── .dockerignore            # Exclude __pycache__, .venv, etc.
│   │   └── entrypoint.sh            # Startup script (migrations + uvicorn)
│   └── database/
│       └── init-scripts/             # Optional: Database initialization SQL
├── k8s/                               # Kubernetes manifests (AI-generated)
│   ├── namespace.yaml                # todo-app namespace
│   ├── frontend/
│   │   ├── deployment.yaml          # Frontend Deployment
│   │   ├── service.yaml             # Frontend Service (ClusterIP)
│   │   └── configmap.yaml           # Frontend environment config
│   ├── backend/
│   │   ├── deployment.yaml          # Backend Deployment
│   │   ├── service.yaml             # Backend Service (ClusterIP)
│   │   ├── configmap.yaml           # Backend environment config
│   │   └── secret.yaml              # Backend secrets (JWT, OpenAI key)
│   ├── database/
│   │   ├── statefulset.yaml         # PostgreSQL StatefulSet
│   │   ├── service.yaml             # Database Service (Headless)
│   │   ├── pvc.yaml                 # PersistentVolumeClaim
│   │   └── secret.yaml              # Database credentials
│   └── ingress.yaml                  # Ingress for external access
├── helm/                              # Helm chart (AI-generated)
│   └── todo-app/
│       ├── Chart.yaml                # Chart metadata
│       ├── values.yaml               # Default values (dev profile)
│       ├── values-dev.yaml           # Development overrides
│       ├── values-test.yaml          # Testing overrides
│       └── templates/
│           ├── namespace.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── frontend-configmap.yaml
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── backend-configmap.yaml
│           ├── backend-secret.yaml
│           ├── database-statefulset.yaml
│           ├── database-service.yaml
│           ├── database-pvc.yaml
│           ├── database-secret.yaml
│           ├── ingress.yaml
│           ├── _helpers.tpl          # Template helpers
│           └── NOTES.txt             # Post-install instructions
├── scripts/                           # Automation scripts
│   ├── setup-minikube.sh             # Minikube initialization
│   ├── setup-minikube.bat            # Windows version
│   ├── build-images.sh               # Docker image building
│   ├── build-images.bat              # Windows version
│   ├── deploy.sh                     # One-command deployment
│   ├── deploy.bat                    # Windows version
│   ├── cleanup.sh                    # Environment teardown
│   ├── cleanup.bat                   # Windows version
│   ├── validate-prerequisites.sh     # Check Docker/Minikube/kubectl/Helm
│   └── validate-prerequisites.bat    # Windows version
├── docs/                              # Documentation
│   ├── SETUP.md                      # Prerequisites and setup guide
│   ├── DEPLOYMENT.md                 # Deployment instructions
│   ├── TROUBLESHOOTING.md            # Common issues and solutions
│   ├── SCALING.md                    # Scaling guide
│   └── ARCHITECTURE.md               # Architecture overview
├── tests/                             # Infrastructure tests
│   ├── helm-lint.sh                  # Helm chart validation
│   ├── k8s-validate.sh               # Kubernetes manifest validation
│   └── deployment-test.sh            # End-to-end deployment test
├── .env.example                       # Environment variables template
├── docker-compose.yml                 # Optional: Local Docker Compose testing
└── README.md                          # Phase IV overview

# Phase III application code (copied, not modified)
phase-4-kubernetes/app/
├── frontend/                          # Copied from phase-3-ai-chatbot/frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js
└── backend/                           # Copied from phase-3-ai-chatbot/backend
    ├── app/
    ├── alembic/
    ├── tests/
    ├── requirements.txt
    ├── alembic.ini
    └── pytest.ini
```

**Structure Decision**: Web application structure (Option 2) with Phase IV isolation. The `phase-4-kubernetes/` directory contains all containerization and orchestration artifacts, while `phase-4-kubernetes/app/` contains copied Phase III application code. This ensures Phase III remains unchanged and Phase IV can be developed/tested independently.

## Complexity Tracking

> **No violations detected. This section is not applicable.**

All constitution checks passed without requiring justification for complexity.

## Phase 0: Research & Technology Decisions

### Research Areas

The following areas require research to resolve technical decisions:

1. **Docker Multi-Stage Build Optimization**
   - Research best practices for Next.js production builds in Docker
   - Research FastAPI Python 3.11 slim image optimization
   - Determine optimal layer caching strategies

2. **Kubernetes Resource Limits**
   - Research appropriate CPU/memory requests and limits for Next.js frontend
   - Research appropriate CPU/memory requests and limits for FastAPI backend
   - Research PostgreSQL resource requirements for development workloads

3. **Helm Chart Best Practices**
   - Research Helm chart structure for multi-service applications
   - Research values.yaml parameterization patterns
   - Research Helm hooks for database migrations

4. **Health Check Patterns**
   - Research liveness vs. readiness probe best practices
   - Research appropriate probe intervals and timeouts
   - Research health check endpoints for Next.js and FastAPI

5. **Persistent Volume Configuration**
   - Research PersistentVolume vs. PersistentVolumeClaim patterns
   - Research StorageClass options for Minikube
   - Research backup/restore strategies for local development

6. **Ingress Configuration**
   - Research NGINX Ingress Controller setup for Minikube
   - Research path-based routing for frontend/backend
   - Research TLS/SSL configuration for local development

7. **AI Tool Integration**
   - Research Docker AI (Gordon) capabilities and limitations
   - Research kubectl-ai command patterns
   - Research kagent integration for cluster management

### Research Deliverable

All research findings will be documented in `research.md` with:
- Decision: What was chosen
- Rationale: Why it was chosen
- Alternatives considered: What else was evaluated
- Implementation guidance: How to apply the decision

## Phase 1: Design & Contracts

### Data Model Entities

The following entities represent the deployment configuration and runtime state:

1. **Deployment Configuration**
   - Helm values.yaml structure
   - Service replica counts
   - Resource limits and requests
   - Environment variables
   - Image tags and registry locations

2. **Service Instance**
   - Pod metadata (name, namespace, labels)
   - Container specifications
   - Health check configuration
   - Resource consumption metrics

3. **Health Check**
   - Liveness probe configuration
   - Readiness probe configuration
   - Startup probe configuration (if needed)
   - Health check endpoints

4. **Configuration Profile**
   - Development values (values-dev.yaml)
   - Testing values (values-test.yaml)
   - Environment-specific overrides

5. **Deployment Artifact**
   - Docker images (frontend, backend, database)
   - Kubernetes manifests
   - Helm chart package
   - Version tags

### API Contracts

Phase IV does not introduce new application APIs. All contracts are infrastructure-level:

1. **Kubernetes Resource Contracts** (in `contracts/` directory)
   - Deployment resource specification
   - Service resource specification
   - ConfigMap resource specification
   - Secret resource specification
   - Helm values.yaml schema

2. **Health Check Endpoints** (existing Phase III endpoints)
   - Frontend: `GET /` (Next.js default)
   - Backend: `GET /health` (existing endpoint)
   - Database: PostgreSQL connection check

3. **Service Communication**
   - Frontend → Backend: HTTP via Kubernetes Service DNS
   - Backend → Database: PostgreSQL connection via Service DNS

### Design Deliverables

Phase 1 will produce:
- `data-model.md`: Detailed deployment configuration entities
- `contracts/`: Kubernetes resource contract specifications
- `quickstart.md`: Step-by-step getting started guide

## Phase 2: Task Breakdown

Task breakdown will be generated by `/sp.tasks` command after Phase 1 completion. Tasks will follow the 7-step SP-PLAN structure:

1. Repository & Folder Validation
2. Containerization (Docker AI / Gordon)
3. Local Kubernetes Environment (Minikube)
4. Kubernetes Manifests via AI
5. Helm Chart Generation
6. AI Ops with kubectl-ai & kagent
7. Verification & Demo Readiness

## Architectural Decisions

### Decision 1: Container Base Images

**Decision**: Use official slim images
- Frontend: `node:18-alpine` (multi-stage build)
- Backend: `python:3.11-slim`
- Database: `postgres:15-alpine`

**Rationale**:
- Alpine/slim images reduce image size and attack surface
- Official images ensure security updates and compatibility
- Multi-stage builds for frontend minimize production image size

**Alternatives Considered**:
- Full images (node:18, python:3.11): Larger size, unnecessary packages
- Distroless images: More complex, harder to debug

### Decision 2: Database Strategy

**Decision**: PostgreSQL StatefulSet with PersistentVolume

**Rationale**:
- StatefulSet provides stable network identity and persistent storage
- PersistentVolume ensures data survives pod restarts
- PostgreSQL aligns with Phase III production configuration

**Alternatives Considered**:
- SQLite in-memory: Data loss on restart, not production-like
- External managed database: Adds complexity, not local-first

### Decision 3: Service Exposure

**Decision**: Ingress with path-based routing

**Rationale**:
- Single entry point for frontend and backend
- Path-based routing (`/` → frontend, `/api` → backend)
- Mimics production deployment patterns

**Alternatives Considered**:
- NodePort services: Requires multiple ports, less production-like
- LoadBalancer: Not available in Minikube without tunnel

### Decision 4: Configuration Management

**Decision**: ConfigMaps for non-sensitive, Secrets for sensitive data

**Rationale**:
- Kubernetes-native configuration management
- Secrets encrypted at rest (Minikube default)
- Easy to override via Helm values

**Alternatives Considered**:
- Environment variables in Dockerfile: Not flexible, requires rebuild
- External secret management (Vault): Overkill for local development

### Decision 5: Helm Chart Structure

**Decision**: Single chart with subcharts for each service

**Rationale**:
- Single `helm install` command deploys entire stack
- Subcharts allow independent versioning if needed
- Values.yaml provides centralized configuration

**Alternatives Considered**:
- Separate charts per service: More complex, multiple install commands
- Raw Kubernetes manifests: No parameterization, less flexible

## Risk Mitigation Strategies

### Technical Risks

1. **Minikube Resource Constraints**
   - Mitigation: Document minimum requirements (8GB RAM, 20GB disk)
   - Mitigation: Implement resource limits in Kubernetes manifests
   - Mitigation: Provide resource optimization guide in documentation

2. **Container Image Size**
   - Mitigation: Use multi-stage builds for frontend
   - Mitigation: Use slim/alpine base images
   - Mitigation: Implement .dockerignore to exclude unnecessary files

3. **Network Connectivity Issues**
   - Mitigation: Implement retry logic in deployment scripts
   - Mitigation: Support offline deployment with pre-pulled images
   - Mitigation: Provide clear error messages for network failures

4. **Port Conflicts**
   - Mitigation: Use Kubernetes Services (ClusterIP) for internal communication
   - Mitigation: Use Ingress for external access (single port)
   - Mitigation: Document port requirements in setup guide

### Process Risks

1. **Lack of Kubernetes Expertise**
   - Mitigation: Provide comprehensive quickstart.md guide
   - Mitigation: Create troubleshooting.md with common issues
   - Mitigation: Use AI tools (kubectl-ai, kagent) to simplify operations

2. **Inconsistent Deployment**
   - Mitigation: Version control all deployment artifacts
   - Mitigation: Provide validation scripts (validate-prerequisites.sh)
   - Mitigation: Use Helm for reproducible deployments

3. **AI Tool Unavailability**
   - Mitigation: Provide fallback manual commands in documentation
   - Mitigation: Document both AI-assisted and manual workflows
   - Mitigation: Ensure core functionality works without AI tools

## Success Metrics

The following metrics will be tracked to validate Phase IV success:

1. **Deployment Time**: <10 minutes from clean environment
2. **First-Attempt Success Rate**: 95%+ when prerequisites met
3. **Service Startup Time**: <5 minutes to ready status
4. **Cross-Platform Compatibility**: Tested on Windows, macOS, Linux
5. **Resource Usage**: Within 8GB RAM, 20GB disk limits
6. **Health Check Accuracy**: <10 seconds to detect failures
7. **Scaling Speed**: <1 minute to add/remove replicas
8. **Data Persistence**: Zero data loss during restarts
9. **Documentation Quality**: New developers deploy successfully without assistance
10. **Troubleshooting Efficiency**: <30 seconds to access logs

## Next Steps

1. **Execute Phase 0**: Generate `research.md` with technology decisions
2. **Execute Phase 1**: Generate `data-model.md`, `contracts/`, and `quickstart.md`
3. **Run `/sp.tasks`**: Generate detailed task breakdown in `tasks.md`
4. **Begin Implementation**: Follow task-driven development workflow

## Notes

- All infrastructure artifacts will be AI-generated (no manual YAML/Dockerfile writing)
- Phase III application code will be copied, not modified
- Deployment must work on Windows, macOS, and Linux
- Helm chart designed for Phase V cloud migration (reusable)
- Documentation must enable deployment without Kubernetes expertise
