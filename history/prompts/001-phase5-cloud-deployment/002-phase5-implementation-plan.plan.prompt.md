---
id: 002
title: Phase V Cloud Deployment Implementation Plan
stage: plan
date: 2026-02-10
surface: agent
model: claude-opus-4-6
feature: 001-phase5-cloud-deployment
branch: 001-phase5-cloud-deployment
user: vikram
command: /sp.plan
labels: ["phase5", "cloud-deployment", "event-driven", "implementation-plan", "dapr", "redpanda", "kubernetes"]
links:
  spec: specs/001-phase5-cloud-deployment/spec.md
  plan: specs/001-phase5-cloud-deployment/plan.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase5-cloud-deployment/plan.md
  - phase-1-cli-app/src/cli/menu.py
tests:
  - Constitution check validation (all gates passed)
  - Technology stack decisions validated
---

## Prompt

User requested creation of Phase V implementation plan with detailed execution stages:

Transform the Todo Chatbot application from Phase IV (Minikube) into production-grade, event-driven, decoupled microservices system using:
- Managed Kubernetes (DOKS)
- Event-driven architecture with Redpanda Cloud
- Dapr sidecar pattern for infrastructure abstraction
- Advanced Todo features (recurring tasks, due dates, reminders, priorities, tags, search/filter)
- Automated CI/CD pipeline
- Production-grade observability and TLS

User also requested enhancement to Phase I CLI to display ASCII art banner similar to Claude Code.

## Response

Created comprehensive Phase V implementation plan with:

**8 Implementation Stages** (35-60 hours total):
- Stage 0: Preparation (1-2 hours)
- Stage 1: Advanced Todo Features (6-12 hours)
- Stage 2: Redpanda Cloud Setup (1-2 hours)
- Stage 3: Dapr Integration (4-8 hours)
- Stage 4: Event-Driven Refactoring (8-15 hours)
- Stage 5: Local Deployment (3-6 hours)
- Stage 6: Cloud Deployment (4-8 hours)
- Stage 7: CI/CD Pipeline (3-5 hours)
- Stage 8: Polish & Documentation (2-4 hours)

**Technology Stack Decisions**:
- Event Streaming: Redpanda Cloud (Kafka-compatible, serverless, free tier)
- Service Runtime: Dapr (portable abstractions, built-in resilience)
- Database: Neon PostgreSQL (serverless, scale-to-zero)
- Kubernetes: DOKS (managed, affordable)
- CI/CD: GitHub Actions (native integration)
- TLS: cert-manager + Let's Encrypt (automatic renewal)
- Search: PostgreSQL FTS (no additional infrastructure)
- Real-time: WebSocket + Dapr (low latency, event-driven)

**Architecture Components**:
- 4 new microservices: recurring-task-service, notification-service, websocket-service, audit-service
- Extended backend with new features and Dapr integration
- Enhanced frontend with new UI components
- Kubernetes manifests with Kustomize overlays
- Helm charts extended from Phase IV

**Constitution Check Results**:
- ✅ Spec-Driven Development: PASS
- ✅ Strict Data Model Compliance: PASS with EXTENSION (justified)
- ✅ Phase Isolation & Forward Compatibility: PASS
- ✅ Feature Completeness: PASS
- ✅ Code Generation & Validation: PASS

**Additional Enhancement**:
- Added ASCII art banner to Phase I CLI application
- Banner displays "TODO APP" on startup
- Cross-platform compatible (ASCII-only characters)
- Enhances user experience similar to Claude Code

## Outcome

- ✅ Impact: Comprehensive implementation plan created with 8 stages, technology decisions, architecture design, and 35-60 hour timeline
- 📁 Files: Created plan.md (647 lines), enhanced Phase I CLI menu.py
- 🔁 Next prompts: /sp.tasks to generate actionable implementation tasks
- 🧠 Reflection: Plan successfully balances technical complexity (event-driven architecture, microservices, Dapr) with practical implementation stages. Constitution checks passed with justified extensions for schema and architecture. Ready for task generation and implementation.

## Evaluation notes

- Failure modes observed: Initial Write tool errors (missing parameters) - resolved by properly structuring tool calls
- Graders run and results: Constitution check - PASS (all 5 gates passed with justified extensions)
- Prompt variant: Standard /sp.plan workflow with user-provided execution stages
- Next experiment: Proceed to /sp.tasks to validate task generation from comprehensive plan
