# Hackathon Q4 - Todo Application

A comprehensive todo management application built across 5 progressive phases, from a simple CLI app to a production-ready cloud-native distributed system.

## Project Overview

This hackathon project demonstrates full-stack development capabilities by building a todo application through five increasingly complex phases. Each phase builds upon the previous one, introducing new technologies and architectural patterns.

**Total Points**: 1000
**Timeline**: Dec 7, 2025 - Jan 18, 2026
**Development Approach**: Spec-Driven Development (SDD) with Claude Code

## Phases

| Phase | Description | Technology Stack | Points | Due Date | Status |
|-------|-------------|-----------------|--------|----------|--------|
| **[Phase I](./phase-1-cli-app/)** | In-Memory Python Console App | Python 3.13+ | 100 | Dec 7, 2025 | ✅ Complete |
| **[Phase II](./phase-2-web-app/)** | Full-Stack Web Application | Next.js, FastAPI, SQLModel, Neon DB | 150 | Dec 14, 2025 | 🔜 Planned |
| **[Phase III](./phase-3-ai-chatbot/)** | AI-Powered Todo Chatbot | OpenAI ChatKit, Agents SDK, MCP SDK | 200 | Dec 21, 2025 | 🔜 Planned |
| **[Phase IV](./phase-4-kubernetes/)** | Local Kubernetes Deployment | Docker, Minikube, Helm, kubectl-ai, kagent | 250 | Jan 4, 2026 | 🔜 Planned |
| **[Phase V](./phase-5-cloud-deployment/)** | Advanced Cloud Deployment | Kafka, Dapr, DigitalOcean DOKS | 300 | Jan 18, 2026 | 🔜 Planned |

## Phase Details

### Phase I: In-Memory Python Console App ✅

**Status**: Complete (100/100 points)

A menu-driven CLI application with full CRUD operations, filtering, date support, and session tracking. Built with Python standard library only, following a three-layer architecture.

**Key Features**:
- Full CRUD operations for todos
- Filter by status, priority, and tags
- Date support with multiple formats
- Session tracking and statistics
- Comprehensive input validation

**[View Phase I Details →](./phase-1-cli-app/)**

---

### Phase II: Full-Stack Web Application 🔜

**Status**: Planned (150 points)

Transform the CLI app into a modern web application with a Next.js frontend, FastAPI backend, and PostgreSQL database.

**Key Features**:
- Modern React UI with Tailwind CSS
- RESTful API with FastAPI
- Database persistence with Neon DB
- User authentication (JWT)
- Multi-user support

**Technology Stack**: Next.js 14, FastAPI, SQLModel, Neon DB (PostgreSQL)

**[View Phase II Details →](./phase-2-web-app/)**

---

### Phase III: AI-Powered Todo Chatbot 🔜

**Status**: Planned (200 points)

Add an AI-powered conversational interface for natural language todo management using OpenAI's latest technologies.

**Key Features**:
- Natural language todo management
- Conversational UI with OpenAI ChatKit
- Custom AI agents with Agents SDK
- Model Context Protocol (MCP) integration
- Smart suggestions and recommendations

**Technology Stack**: OpenAI ChatKit, Agents SDK, Official MCP SDK, GPT-4

**[View Phase III Details →](./phase-3-ai-chatbot/)**

---

### Phase IV: Local Kubernetes Deployment 🔜

**Status**: Planned (250 points)

Containerize the application and deploy to a local Kubernetes cluster with AI-powered management tools.

**Key Features**:
- Docker containerization
- Kubernetes orchestration with Minikube
- Helm charts for deployment
- kubectl-ai for natural language commands
- kagent for intelligent cluster management
- Prometheus & Grafana monitoring

**Technology Stack**: Docker, Minikube, Helm, kubectl-ai, kagent, Prometheus, Grafana

**[View Phase IV Details →](./phase-4-kubernetes/)**

---

### Phase V: Advanced Cloud Deployment 🔜

**Status**: Planned (300 points)

Deploy to production cloud infrastructure with event-driven architecture and enterprise-grade features.

**Key Features**:
- Event streaming with Apache Kafka
- Microservices with Dapr
- CQRS and event sourcing
- Multi-region deployment on DigitalOcean
- Advanced observability and monitoring
- Production security and compliance

**Technology Stack**: Apache Kafka, Dapr, DigitalOcean Kubernetes (DOKS), Terraform, Istio

**[View Phase V Details →](./phase-5-cloud-deployment/)**

## Project Structure

```
hackathon-02-todo-app/
├── phase-1-cli-app/           # ✅ Phase I: Python CLI (Complete)
│   ├── src/                   # Source code
│   ├── specs/                 # Specifications and design docs
│   ├── USAGE_GUIDE.md        # User guide
│   └── README.md             # Phase I documentation
│
├── phase-2-web-app/           # 🔜 Phase II: Web App (Planned)
│   ├── frontend/             # Next.js application
│   ├── backend/              # FastAPI application
│   └── README.md             # Phase II documentation
│
├── phase-3-ai-chatbot/        # 🔜 Phase III: AI Chatbot (Planned)
│   ├── frontend/             # Chat UI
│   ├── backend/              # AI agents
│   └── README.md             # Phase III documentation
│
├── phase-4-kubernetes/        # 🔜 Phase IV: Kubernetes (Planned)
│   ├── docker/               # Dockerfiles
│   ├── k8s/                  # Kubernetes manifests
│   ├── helm/                 # Helm charts
│   └── README.md             # Phase IV documentation
│
├── phase-5-cloud-deployment/  # 🔜 Phase V: Cloud (Planned)
│   ├── infrastructure/       # Terraform/Pulumi
│   ├── kafka/                # Kafka configuration
│   ├── dapr/                 # Dapr components
│   ├── services/             # Microservices
│   └── README.md             # Phase V documentation
│
├── .specify/                  # Spec-Kit Plus templates
├── history/                   # Prompt history and ADRs
├── CLAUDE.md                 # Claude Code instructions
└── README.md                 # This file
```

## Getting Started

### Phase I (Current)

The CLI application is ready to run:

```bash
cd phase-1-cli-app
python src/main.py
```

See [Phase I README](./phase-1-cli-app/README.md) for detailed instructions.

### Future Phases

Each subsequent phase will build upon the previous one. Setup instructions will be added as each phase is implemented.

## Development Approach

This project follows **Spec-Driven Development (SDD)** using Claude Code and Spec-Kit Plus:

1. **Specification** - Define requirements and user stories
2. **Planning** - Create architectural design and technical plan
3. **Tasks** - Break down into testable, dependency-ordered tasks
4. **Implementation** - Execute tasks with continuous validation
5. **Documentation** - Generate comprehensive guides and docs

All design artifacts, prompts, and architectural decisions are tracked in the `history/` directory.

## Technology Evolution

| Aspect | Phase I | Phase II | Phase III | Phase IV | Phase V |
|--------|---------|----------|-----------|----------|---------|
| **Interface** | CLI | Web UI | AI Chat | Web UI | Web UI |
| **Storage** | In-Memory | PostgreSQL | PostgreSQL | PostgreSQL | Event Store |
| **Architecture** | Monolith | Monolith | Monolith | Containers | Microservices |
| **Deployment** | Local | Local | Local | Kubernetes | Cloud |
| **Scale** | Single User | Multi-User | Multi-User | Multi-User | Enterprise |

## Key Achievements

### Phase I ✅
- ✅ 63/63 tasks completed (100%)
- ✅ All 27 functional requirements satisfied
- ✅ All 7 success criteria met
- ✅ Comprehensive documentation
- ✅ Forward-compatible service layer

## Prerequisites

### Phase I
- Python 3.13+

### Phase II (Upcoming)
- Node.js 18+
- Python 3.13+
- Neon DB account

### Phase III (Upcoming)
- OpenAI API key
- All Phase II prerequisites

### Phase IV (Upcoming)
- Docker Desktop
- Minikube
- Helm 3+
- kubectl

### Phase V (Upcoming)
- DigitalOcean account
- Terraform or Pulumi
- All Phase IV prerequisites

## Documentation

Each phase contains detailed documentation:

- **README.md** - Overview, features, and getting started
- **specs/** - Specifications, plans, and design documents
- **USAGE_GUIDE.md** - Comprehensive usage instructions (Phase I)

Project-wide documentation:

- **[CLAUDE.md](./CLAUDE.md)** - Claude Code development guidelines
- **[history/prompts/](./history/prompts/)** - Prompt History Records (PHRs)
- **[history/adr/](./history/adr/)** - Architecture Decision Records (ADRs)

## Contributing

This is a hackathon project demonstrating progressive complexity in application development. Each phase is self-contained and can be studied independently.

## License

[Add license information]

---

**Current Phase**: Phase I (Complete)
**Next Phase**: Phase II (Full-Stack Web Application)
**Last Updated**: 2026-01-10
