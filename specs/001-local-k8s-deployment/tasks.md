# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/001-local-k8s-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT explicitly requested in the specification. Infrastructure validation will be done through deployment testing and health checks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Phase IV Directory**: `phase-4-kubernetes/` at repository root
- **Docker artifacts**: `phase-4-kubernetes/docker/`
- **Kubernetes manifests**: `phase-4-kubernetes/k8s/`
- **Helm charts**: `phase-4-kubernetes/helm/`
- **Scripts**: `phase-4-kubernetes/scripts/`
- **Documentation**: `phase-4-kubernetes/docs/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure creation

- [ ] T001 Create phase-4-kubernetes/ directory structure per plan.md
- [ ] T002 [P] Copy Phase III frontend code to phase-4-kubernetes/app/frontend/
- [ ] T003 [P] Copy Phase III backend code to phase-4-kubernetes/app/backend/
- [ ] T004 [P] Create .dockerignore files for frontend in phase-4-kubernetes/docker/frontend/.dockerignore
- [ ] T005 [P] Create .dockerignore files for backend in phase-4-kubernetes/docker/backend/.dockerignore
- [ ] T006 [P] Create .env.example file in phase-4-kubernetes/.env.example
- [ ] T007 [P] Create README.md for Phase IV in phase-4-kubernetes/README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Generate frontend Dockerfile using AI in phase-4-kubernetes/docker/frontend/Dockerfile
- [ ] T009 Generate backend Dockerfile using AI in phase-4-kubernetes/docker/backend/Dockerfile
- [ ] T010 [P] Create backend entrypoint script in phase-4-kubernetes/docker/backend/entrypoint.sh
- [ ] T011 [P] Create Kubernetes namespace manifest in phase-4-kubernetes/k8s/namespace.yaml
- [ ] T012 [P] Create prerequisite validation script (Linux/macOS) in phase-4-kubernetes/scripts/validate-prerequisites.sh
- [ ] T013 [P] Create prerequisite validation script (Windows) in phase-4-kubernetes/scripts/validate-prerequisites.bat
- [ ] T014 [P] Create Minikube setup script (Linux/macOS) in phase-4-kubernetes/scripts/setup-minikube.sh
- [ ] T015 [P] Create Minikube setup script (Windows) in phase-4-kubernetes/scripts/setup-minikube.bat

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - One-Command Local Deployment (Priority: P1) 🎯 MVP

**Goal**: Deploy entire todo application stack (frontend, backend, database) to local Kubernetes with a single command

**Independent Test**: Run deployment command on clean machine with prerequisites installed, verify all services accessible and functional within 5 minutes

### Implementation for User Story 1

- [ ] T016 [P] [US1] Generate frontend Deployment manifest using AI in phase-4-kubernetes/k8s/frontend/deployment.yaml
- [ ] T017 [P] [US1] Generate frontend Service manifest using AI in phase-4-kubernetes/k8s/frontend/service.yaml
- [ ] T018 [P] [US1] Generate frontend ConfigMap manifest using AI in phase-4-kubernetes/k8s/frontend/configmap.yaml
- [ ] T019 [P] [US1] Generate backend Deployment manifest using AI in phase-4-kubernetes/k8s/backend/deployment.yaml
- [ ] T020 [P] [US1] Generate backend Service manifest using AI in phase-4-kubernetes/k8s/backend/service.yaml
- [ ] T021 [P] [US1] Generate backend ConfigMap manifest using AI in phase-4-kubernetes/k8s/backend/configmap.yaml
- [ ] T022 [P] [US1] Generate backend Secret manifest using AI in phase-4-kubernetes/k8s/backend/secret.yaml
- [ ] T023 [P] [US1] Generate database StatefulSet manifest using AI in phase-4-kubernetes/k8s/database/statefulset.yaml
- [ ] T024 [P] [US1] Generate database Service manifest using AI in phase-4-kubernetes/k8s/database/service.yaml
- [ ] T025 [P] [US1] Generate database PVC manifest using AI in phase-4-kubernetes/k8s/database/pvc.yaml
- [ ] T026 [P] [US1] Generate database Secret manifest using AI in phase-4-kubernetes/k8s/database/secret.yaml
- [ ] T027 [P] [US1] Generate Ingress manifest using AI in phase-4-kubernetes/k8s/ingress.yaml
- [ ] T028 [US1] Create Helm Chart.yaml in phase-4-kubernetes/helm/todo-app/Chart.yaml
- [ ] T029 [US1] Create Helm values.yaml in phase-4-kubernetes/helm/todo-app/values.yaml
- [ ] T030 [P] [US1] Create Helm frontend deployment template in phase-4-kubernetes/helm/todo-app/templates/frontend-deployment.yaml
- [ ] T031 [P] [US1] Create Helm frontend service template in phase-4-kubernetes/helm/todo-app/templates/frontend-service.yaml
- [ ] T032 [P] [US1] Create Helm frontend configmap template in phase-4-kubernetes/helm/todo-app/templates/frontend-configmap.yaml
- [ ] T033 [P] [US1] Create Helm backend deployment template in phase-4-kubernetes/helm/todo-app/templates/backend-deployment.yaml
- [ ] T034 [P] [US1] Create Helm backend service template in phase-4-kubernetes/helm/todo-app/templates/backend-service.yaml
- [ ] T035 [P] [US1] Create Helm backend configmap template in phase-4-kubernetes/helm/todo-app/templates/backend-configmap.yaml
- [ ] T036 [P] [US1] Create Helm backend secret template in phase-4-kubernetes/helm/todo-app/templates/backend-secret.yaml
- [ ] T037 [P] [US1] Create Helm database statefulset template in phase-4-kubernetes/helm/todo-app/templates/database-statefulset.yaml
- [ ] T038 [P] [US1] Create Helm database service template in phase-4-kubernetes/helm/todo-app/templates/database-service.yaml
- [ ] T039 [P] [US1] Create Helm database pvc template in phase-4-kubernetes/helm/todo-app/templates/database-pvc.yaml
- [ ] T040 [P] [US1] Create Helm database secret template in phase-4-kubernetes/helm/todo-app/templates/database-secret.yaml
- [ ] T041 [P] [US1] Create Helm ingress template in phase-4-kubernetes/helm/todo-app/templates/ingress.yaml
- [ ] T042 [P] [US1] Create Helm namespace template in phase-4-kubernetes/helm/todo-app/templates/namespace.yaml
- [ ] T043 [P] [US1] Create Helm helpers template in phase-4-kubernetes/helm/todo-app/templates/_helpers.tpl
- [ ] T044 [P] [US1] Create Helm NOTES.txt in phase-4-kubernetes/helm/todo-app/templates/NOTES.txt
- [ ] T045 [US1] Create Docker image build script (Linux/macOS) in phase-4-kubernetes/scripts/build-images.sh
- [ ] T046 [US1] Create Docker image build script (Windows) in phase-4-kubernetes/scripts/build-images.bat
- [ ] T047 [US1] Create one-command deployment script (Linux/macOS) in phase-4-kubernetes/scripts/deploy.sh
- [ ] T048 [US1] Create one-command deployment script (Windows) in phase-4-kubernetes/scripts/deploy.bat
- [ ] T049 [US1] Test deployment on clean environment and verify all services start within 5 minutes
- [ ] T050 [US1] Verify application UI loads and is fully functional at http://todo.local
- [ ] T051 [US1] Test consecutive deployments succeed without conflicts
- [ ] T052 [US1] Verify all health checks pass and services report ready status

**Checkpoint**: At this point, User Story 1 should be fully functional - complete one-command deployment working

---

## Phase 4: User Story 2 - Environment Reproducibility (Priority: P2)

**Goal**: Ensure deployment is reproducible across different developer machines and operating systems

**Independent Test**: Deploy on multiple machines (Windows, Mac, Linux) with different configurations and verify identical behavior

### Implementation for User Story 2

- [ ] T053 [P] [US2] Create values-dev.yaml for development profile in phase-4-kubernetes/helm/todo-app/values-dev.yaml
- [ ] T054 [P] [US2] Create values-test.yaml for testing profile in phase-4-kubernetes/helm/todo-app/values-test.yaml
- [ ] T055 [US2] Add version tagging to Docker image build scripts in phase-4-kubernetes/scripts/build-images.sh
- [ ] T056 [US2] Add version tagging to Docker image build scripts (Windows) in phase-4-kubernetes/scripts/build-images.bat
- [ ] T057 [P] [US2] Create deployment verification script (Linux/macOS) in phase-4-kubernetes/scripts/verify-deployment.sh
- [ ] T058 [P] [US2] Create deployment verification script (Windows) in phase-4-kubernetes/scripts/verify-deployment.bat
- [ ] T059 [P] [US2] Document environment variables in phase-4-kubernetes/.env.example
- [ ] T060 [P] [US2] Create SETUP.md documentation in phase-4-kubernetes/docs/SETUP.md
- [ ] T061 [P] [US2] Create DEPLOYMENT.md documentation in phase-4-kubernetes/docs/DEPLOYMENT.md
- [ ] T062 [US2] Test deployment on Windows machine and verify identical behavior
- [ ] T063 [US2] Test deployment on macOS machine and verify identical behavior
- [ ] T064 [US2] Test deployment on Linux machine and verify identical behavior
- [ ] T065 [US2] Test environment teardown and redeployment produces identical results
- [ ] T066 [US2] Verify version-controlled artifacts produce consistent deployments

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - reproducible deployment across platforms

---

## Phase 5: User Story 3 - Service Scaling and Resource Management (Priority: P3)

**Goal**: Enable independent scaling of services and resource usage monitoring

**Independent Test**: Scale services to different replica counts and measure response times and resource consumption

### Implementation for User Story 3

- [ ] T067 [P] [US3] Add HPA (Horizontal Pod Autoscaler) template to Helm chart in phase-4-kubernetes/helm/todo-app/templates/frontend-hpa.yaml
- [ ] T068 [P] [US3] Add HPA template for backend in phase-4-kubernetes/helm/todo-app/templates/backend-hpa.yaml
- [ ] T069 [P] [US3] Configure resource requests and limits in Helm values.yaml
- [ ] T070 [P] [US3] Create scaling guide documentation in phase-4-kubernetes/docs/SCALING.md
- [ ] T071 [US3] Create scaling helper script (Linux/macOS) in phase-4-kubernetes/scripts/scale-service.sh
- [ ] T072 [US3] Create scaling helper script (Windows) in phase-4-kubernetes/scripts/scale-service.bat
- [ ] T073 [P] [US3] Add resource monitoring commands to quickstart guide
- [ ] T074 [US3] Test scaling backend service to 3 replicas and verify load handling
- [ ] T075 [US3] Test pod failure scenario and verify traffic routes to healthy replicas
- [ ] T076 [US3] Verify CPU and memory metrics are visible via kubectl top
- [ ] T077 [US3] Test resource limit enforcement and verify exhaustion prevention

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - scaling and resource management functional

---

## Phase 6: User Story 4 - Rapid Troubleshooting and Debugging (Priority: P4)

**Goal**: Enable quick identification and diagnosis of issues without deep Kubernetes expertise

**Independent Test**: Introduce deliberate failures and verify diagnostic information is accessible and actionable

### Implementation for User Story 4

- [ ] T078 [P] [US4] Create troubleshooting guide in phase-4-kubernetes/docs/TROUBLESHOOTING.md
- [ ] T079 [P] [US4] Create log viewing helper script (Linux/macOS) in phase-4-kubernetes/scripts/view-logs.sh
- [ ] T080 [P] [US4] Create log viewing helper script (Windows) in phase-4-kubernetes/scripts/view-logs.bat
- [ ] T081 [P] [US4] Create health check script (Linux/macOS) in phase-4-kubernetes/scripts/check-health.sh
- [ ] T082 [P] [US4] Create health check script (Windows) in phase-4-kubernetes/scripts/check-health.bat
- [ ] T083 [P] [US4] Add detailed error messages to deployment scripts
- [ ] T084 [P] [US4] Add diagnostic commands to Helm NOTES.txt
- [ ] T085 [P] [US4] Document common failure scenarios in TROUBLESHOOTING.md
- [ ] T086 [US4] Test service failure scenario and verify clear error messages
- [ ] T087 [US4] Test log access and verify diagnostic information is available
- [ ] T088 [US4] Test health check failure and verify failure reasons are reported
- [ ] T089 [US4] Test deployment failure and verify actionable steps are provided

**Checkpoint**: At this point, User Stories 1-4 should all work independently - troubleshooting capabilities functional

---

## Phase 7: User Story 5 - Configuration Management (Priority: P5)

**Goal**: Enable management of environment-specific configurations separately from deployment code

**Independent Test**: Deploy with different configuration sets and verify services use correct values

### Implementation for User Story 5

- [ ] T090 [P] [US5] Create configuration management documentation in phase-4-kubernetes/docs/CONFIGURATION.md
- [ ] T091 [P] [US5] Add configuration profile selection to deployment scripts
- [ ] T092 [P] [US5] Create secret management helper script (Linux/macOS) in phase-4-kubernetes/scripts/manage-secrets.sh
- [ ] T093 [P] [US5] Create secret management helper script (Windows) in phase-4-kubernetes/scripts/manage-secrets.bat
- [ ] T094 [P] [US5] Document secret rotation procedures in CONFIGURATION.md
- [ ] T095 [P] [US5] Add ConfigMap update examples to documentation
- [ ] T096 [US5] Test deployment with development configuration profile
- [ ] T097 [US5] Test deployment with testing configuration profile
- [ ] T098 [US5] Verify secrets are encrypted and not visible in plain text
- [ ] T099 [US5] Test configuration update without full redeployment

**Checkpoint**: All user stories should now be independently functional - complete configuration management

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T100 [P] Create architecture overview documentation in phase-4-kubernetes/docs/ARCHITECTURE.md
- [ ] T101 [P] Create cleanup script (Linux/macOS) in phase-4-kubernetes/scripts/cleanup.sh
- [ ] T102 [P] Create cleanup script (Windows) in phase-4-kubernetes/scripts/cleanup.bat
- [ ] T103 [P] Add kubectl-ai usage examples to documentation
- [ ] T104 [P] Add kagent usage examples to documentation
- [ ] T105 [P] Create Helm chart validation script in phase-4-kubernetes/tests/helm-lint.sh
- [ ] T106 [P] Create Kubernetes manifest validation script in phase-4-kubernetes/tests/k8s-validate.sh
- [ ] T107 [P] Create end-to-end deployment test script in phase-4-kubernetes/tests/deployment-test.sh
- [ ] T108 [P] Add docker-compose.yml for local testing in phase-4-kubernetes/docker-compose.yml
- [ ] T109 [P] Update root README.md with Phase IV information
- [ ] T110 Validate all scripts work on Windows, macOS, and Linux
- [ ] T111 Run complete deployment test following quickstart.md
- [ ] T112 Verify deployment time is under 10 minutes from clean environment
- [ ] T113 Verify 95%+ first-attempt success rate with prerequisites met
- [ ] T114 Verify zero data loss during service restarts
- [ ] T115 Final validation: All 5 user stories work independently and together

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Requires US1 deployment working
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Enhances US1 with troubleshooting
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Enhances US1 with configuration flexibility

### Within Each User Story

- Kubernetes manifests before Helm templates
- Helm Chart.yaml and values.yaml before templates
- Templates before deployment scripts
- Deployment scripts before testing
- Core implementation before documentation
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T002-T007) marked [P] can run in parallel
- All Foundational tasks (T010-T015) marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All Kubernetes manifests within a story marked [P] can run in parallel
- All Helm templates within a story marked [P] can run in parallel
- Documentation tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all Kubernetes manifests for User Story 1 together:
Task: "Generate frontend Deployment manifest using AI in phase-4-kubernetes/k8s/frontend/deployment.yaml"
Task: "Generate frontend Service manifest using AI in phase-4-kubernetes/k8s/frontend/service.yaml"
Task: "Generate frontend ConfigMap manifest using AI in phase-4-kubernetes/k8s/frontend/configmap.yaml"
Task: "Generate backend Deployment manifest using AI in phase-4-kubernetes/k8s/backend/deployment.yaml"
Task: "Generate backend Service manifest using AI in phase-4-kubernetes/k8s/backend/service.yaml"
Task: "Generate backend ConfigMap manifest using AI in phase-4-kubernetes/k8s/backend/configmap.yaml"
Task: "Generate backend Secret manifest using AI in phase-4-kubernetes/k8s/backend/secret.yaml"
Task: "Generate database StatefulSet manifest using AI in phase-4-kubernetes/k8s/database/statefulset.yaml"
Task: "Generate database Service manifest using AI in phase-4-kubernetes/k8s/database/service.yaml"
Task: "Generate database PVC manifest using AI in phase-4-kubernetes/k8s/database/pvc.yaml"
Task: "Generate database Secret manifest using AI in phase-4-kubernetes/k8s/database/secret.yaml"
Task: "Generate Ingress manifest using AI in phase-4-kubernetes/k8s/ingress.yaml"

# Launch all Helm templates for User Story 1 together:
Task: "Create Helm frontend deployment template in phase-4-kubernetes/helm/todo-app/templates/frontend-deployment.yaml"
Task: "Create Helm frontend service template in phase-4-kubernetes/helm/todo-app/templates/frontend-service.yaml"
Task: "Create Helm frontend configmap template in phase-4-kubernetes/helm/todo-app/templates/frontend-configmap.yaml"
Task: "Create Helm backend deployment template in phase-4-kubernetes/helm/todo-app/templates/backend-deployment.yaml"
Task: "Create Helm backend service template in phase-4-kubernetes/helm/todo-app/templates/backend-service.yaml"
Task: "Create Helm backend configmap template in phase-4-kubernetes/helm/todo-app/templates/backend-configmap.yaml"
Task: "Create Helm backend secret template in phase-4-kubernetes/helm/todo-app/templates/backend-secret.yaml"
Task: "Create Helm database statefulset template in phase-4-kubernetes/helm/todo-app/templates/database-statefulset.yaml"
Task: "Create Helm database service template in phase-4-kubernetes/helm/todo-app/templates/database-service.yaml"
Task: "Create Helm database pvc template in phase-4-kubernetes/helm/todo-app/templates/database-pvc.yaml"
Task: "Create Helm database secret template in phase-4-kubernetes/helm/todo-app/templates/database-secret.yaml"
Task: "Create Helm ingress template in phase-4-kubernetes/helm/todo-app/templates/ingress.yaml"
Task: "Create Helm namespace template in phase-4-kubernetes/helm/todo-app/templates/namespace.yaml"
Task: "Create Helm helpers template in phase-4-kubernetes/helm/todo-app/templates/_helpers.tpl"
Task: "Create Helm NOTES.txt in phase-4-kubernetes/helm/todo-app/templates/NOTES.txt"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T015) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T016-T052)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready - **This is your MVP!**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Reproducibility added)
4. Add User Story 3 → Test independently → Deploy/Demo (Scaling added)
5. Add User Story 4 → Test independently → Deploy/Demo (Troubleshooting added)
6. Add User Story 5 → Test independently → Deploy/Demo (Configuration management added)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T015)
2. Once Foundational is done:
   - Developer A: User Story 1 (T016-T052)
   - Developer B: User Story 2 (T053-T066) - can start after US1 basics
   - Developer C: User Story 3 (T067-T077) - can start after US1 basics
3. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 115

**Tasks by Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 8 tasks
- Phase 3 (US1 - One-Command Deployment): 37 tasks
- Phase 4 (US2 - Environment Reproducibility): 14 tasks
- Phase 5 (US3 - Service Scaling): 11 tasks
- Phase 6 (US4 - Rapid Troubleshooting): 12 tasks
- Phase 7 (US5 - Configuration Management): 10 tasks
- Phase 8 (Polish): 16 tasks

**Parallel Opportunities**: 78 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Run deployment command, verify all services accessible within 5 minutes
- US2: Deploy on Windows/Mac/Linux, verify identical behavior
- US3: Scale services, measure response times and resource consumption
- US4: Introduce failures, verify diagnostic information accessible
- US5: Deploy with different configs, verify services use correct values

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 52 tasks

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All infrastructure artifacts generated via AI tools (no manual YAML/Dockerfile writing)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Phase III application code remains unchanged (copied, not modified)
- All scripts must work on Windows, macOS, and Linux
