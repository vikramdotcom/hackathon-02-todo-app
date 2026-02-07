# Architecture Overview - Phase IV Local Kubernetes Deployment

**Version**: 1.0
**Last Updated**: February 7, 2026
**Status**: Production-Ready

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Component Overview](#component-overview)
4. [Infrastructure Architecture](#infrastructure-architecture)
5. [Deployment Architecture](#deployment-architecture)
6. [Data Flow](#data-flow)
7. [Security Architecture](#security-architecture)
8. [Scalability & Performance](#scalability--performance)
9. [Monitoring & Observability](#monitoring--observability)
10. [Disaster Recovery](#disaster-recovery)
11. [Technology Stack](#technology-stack)
12. [Design Decisions](#design-decisions)

---

## Executive Summary

Phase IV implements a complete local Kubernetes deployment solution for the Todo App, providing a production-like environment for development, testing, and learning. The architecture supports:

- **One-command deployment** with automated setup
- **Environment reproducibility** across Windows, macOS, and Linux
- **Horizontal scaling** with automatic and manual options
- **Comprehensive troubleshooting** tools and diagnostics
- **Configuration management** with profile-based deployments

### Key Metrics

- **Deployment Time**: < 10 minutes from clean environment
- **Components**: 3 microservices (Frontend, Backend, Database)
- **Scalability**: Horizontal pod autoscaling (1-10 replicas)
- **Availability**: Rolling updates with zero downtime
- **Resource Efficiency**: Configurable profiles (dev/test/prod)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Ingress Controller                          │
│                    (NGINX Ingress)                               │
└────────────┬────────────────────────────┬───────────────────────┘
             │                            │
             │ /                          │ /api
             ▼                            ▼
┌────────────────────────┐    ┌──────────────────────────┐
│   Frontend Service     │    │   Backend Service        │
│   (ClusterIP)          │    │   (ClusterIP)            │
└────────┬───────────────┘    └──────────┬───────────────┘
         │                               │
         │ Load Balance                  │ Load Balance
         ▼                               ▼
┌────────────────────────┐    ┌──────────────────────────┐
│  Frontend Pods (1-10)  │    │  Backend Pods (1-10)     │
│  - Next.js 14          │    │  - FastAPI               │
│  - React 18            │    │  - Python 3.11           │
│  - TypeScript          │    │  - SQLAlchemy            │
└────────────────────────┘    └──────────┬───────────────┘
                                         │
                                         │ PostgreSQL
                                         ▼
                              ┌──────────────────────────┐
                              │   Database Service       │
                              │   (ClusterIP)            │
                              └──────────┬───────────────┘
                                         │
                                         ▼
                              ┌──────────────────────────┐
                              │   Database Pod           │
                              │   - PostgreSQL 15        │
                              │   - Persistent Volume    │
                              └──────────────────────────┘
```

### Network Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Minikube Cluster                            │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Namespace: todo-app                      │ │
│  │                                                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │   Frontend   │  │   Backend    │  │   Database   │    │ │
│  │  │   Pods       │  │   Pods       │  │   Pod        │    │ │
│  │  │              │  │              │  │              │    │ │
│  │  │  Port: 3000  │  │  Port: 8000  │  │  Port: 5432  │    │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │ │
│  │         │                 │                 │             │ │
│  │         ▼                 ▼                 ▼             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │   Service    │  │   Service    │  │   Service    │    │ │
│  │  │  ClusterIP   │  │  ClusterIP   │  │  ClusterIP   │    │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────────┘    │ │
│  │         │                 │                               │ │
│  │         └─────────┬───────┘                               │ │
│  │                   ▼                                       │ │
│  │            ┌──────────────┐                               │ │
│  │            │   Ingress    │                               │ │
│  │            │  todo.local  │                               │ │
│  │            └──────┬───────┘                               │ │
│  └───────────────────┼────────────────────────────────────────┘ │
│                      │                                          │
└──────────────────────┼──────────────────────────────────────────┘
                       │
                       ▼
                ┌──────────────┐
                │  Host System │
                │  todo.local  │
                └──────────────┘
```

---

## Component Overview

### Frontend Component

**Technology**: Next.js 14, React 18, TypeScript, Tailwind CSS

**Responsibilities**:
- User interface rendering
- Client-side routing
- API communication
- State management
- Form validation

**Configuration**:
- Environment: `NEXT_PUBLIC_API_URL`
- Port: 3000
- Health Check: HTTP GET /
- Readiness: HTTP GET /

**Scaling**:
- Horizontal: 1-10 replicas
- Autoscaling: CPU > 70%, Memory > 80%
- Resources: 128Mi-512Mi memory, 100m-500m CPU

### Backend Component

**Technology**: FastAPI, Python 3.11, SQLAlchemy, Alembic

**Responsibilities**:
- REST API endpoints
- Business logic
- Database operations
- Authentication/Authorization
- AI chatbot integration (OpenAI)

**Configuration**:
- Environment: `DATABASE_URL`, `SECRET_KEY`, `OPENAI_API_KEY`
- Port: 8000
- Health Check: HTTP GET /health
- Readiness: HTTP GET /health

**Scaling**:
- Horizontal: 1-10 replicas
- Autoscaling: CPU > 70%, Memory > 80%
- Resources: 256Mi-512Mi memory, 200m-500m CPU

### Database Component

**Technology**: PostgreSQL 15

**Responsibilities**:
- Data persistence
- Transaction management
- Query optimization
- Backup and recovery

**Configuration**:
- Environment: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- Port: 5432
- Health Check: pg_isready
- Readiness: pg_isready

**Storage**:
- Persistent Volume: 1Gi
- Storage Class: standard
- Access Mode: ReadWriteOnce

---

## Infrastructure Architecture

### Kubernetes Resources

#### Deployments

**Frontend Deployment**:
```yaml
Replicas: 1-10 (configurable)
Strategy: RollingUpdate
  MaxSurge: 1
  MaxUnavailable: 0
Resources:
  Requests: 128Mi memory, 100m CPU
  Limits: 512Mi memory, 500m CPU
Probes:
  Liveness: HTTP GET / (30s delay, 10s period)
  Readiness: HTTP GET / (5s delay, 5s period)
```

**Backend Deployment**:
```yaml
Replicas: 1-10 (configurable)
Strategy: RollingUpdate
  MaxSurge: 1
  MaxUnavailable: 0
Resources:
  Requests: 256Mi memory, 200m CPU
  Limits: 512Mi memory, 500m CPU
Probes:
  Liveness: HTTP GET /health (30s delay, 10s period)
  Readiness: HTTP GET /health (5s delay, 5s period)
```

**Database Deployment**:
```yaml
Replicas: 1 (stateful)
Strategy: Recreate
Resources:
  Requests: 256Mi memory, 250m CPU
  Limits: 512Mi memory, 500m CPU
Volume: PersistentVolumeClaim (1Gi)
Probes:
  Liveness: pg_isready (30s delay, 10s period)
  Readiness: pg_isready (5s delay, 5s period)
```

#### Services

**Frontend Service**:
```yaml
Type: ClusterIP
Port: 3000
Selector: app=frontend
```

**Backend Service**:
```yaml
Type: ClusterIP
Port: 8000
Selector: app=backend
```

**Database Service**:
```yaml
Type: ClusterIP
Port: 5432
Selector: app=database
```

#### Ingress

```yaml
Host: todo.local
Rules:
  - Path: /
    Backend: frontend:3000
  - Path: /api
    Backend: backend:8000
Annotations:
  nginx.ingress.kubernetes.io/rewrite-target: /
```

#### ConfigMaps

**Application ConfigMap**:
- Log levels
- CORS origins
- Feature flags
- Application settings

#### Secrets

**Application Secrets**:
- Database URL
- Secret key (JWT/sessions)
- OpenAI API key
- Encryption: base64 (Kubernetes default)

#### Horizontal Pod Autoscalers

**Frontend HPA**:
```yaml
MinReplicas: 1
MaxReplicas: 10
Metrics:
  - CPU: 70%
  - Memory: 80%
```

**Backend HPA**:
```yaml
MinReplicas: 1
MaxReplicas: 10
Metrics:
  - CPU: 70%
  - Memory: 80%
```

---

## Deployment Architecture

### Deployment Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Deployment Process                            │
└─────────────────────────────────────────────────────────────────┘

1. Prerequisites Validation
   ├─ Check Docker installed
   ├─ Check kubectl installed
   ├─ Check Helm installed
   └─ Check Minikube installed

2. Minikube Setup
   ├─ Start Minikube cluster
   ├─ Enable Ingress addon
   ├─ Enable Metrics Server addon
   └─ Configure Docker environment

3. Image Building
   ├─ Build frontend image (multi-stage)
   ├─ Build backend image (multi-stage)
   ├─ Tag with version (git SHA or timestamp)
   └─ Load images into Minikube

4. Helm Deployment
   ├─ Lint Helm chart
   ├─ Select configuration profile (dev/test/prod)
   ├─ Create namespace
   ├─ Install/Upgrade release
   └─ Wait for rollout completion

5. Post-Deployment
   ├─ Verify pod status
   ├─ Check service endpoints
   ├─ Test health endpoints
   └─ Display access information
```

### Configuration Profiles

**Development Profile** (`values-dev.yaml`):
- Purpose: Local development
- Replicas: 1 per service
- Resources: Minimal (128Mi-256Mi)
- Logging: Debug level
- Autoscaling: Disabled

**Testing Profile** (`values-test.yaml`):
- Purpose: Integration testing
- Replicas: 2 per service
- Resources: Standard (256Mi-512Mi)
- Logging: Info level
- Autoscaling: Enabled

**Production Profile** (Future):
- Purpose: Production deployment
- Replicas: 3+ per service
- Resources: High (512Mi-1Gi)
- Logging: Error level
- Autoscaling: Enabled with conservative thresholds

---

## Data Flow

### User Request Flow

```
1. User → Browser
   └─ HTTP Request to http://todo.local

2. Browser → Ingress Controller
   └─ DNS resolution (hosts file)
   └─ HTTP Request to Minikube IP

3. Ingress Controller → Service
   └─ Route based on path:
      - / → Frontend Service
      - /api → Backend Service

4. Service → Pod
   └─ Load balance across available pods
   └─ Round-robin distribution

5. Pod → Response
   └─ Process request
   └─ Return response

6. Response → User
   └─ Through Ingress → Browser
```

### API Request Flow

```
1. Frontend → Backend API
   └─ HTTP Request to /api/todos

2. Backend → Database
   └─ SQL Query via SQLAlchemy
   └─ Connection pooling

3. Database → Backend
   └─ Query results

4. Backend → Frontend
   └─ JSON response

5. Frontend → User
   └─ Render UI update
```

### Database Operations

```
1. Backend → Database Connection
   └─ Connection string from secret
   └─ Connection pooling (5 connections)

2. Backend → Query Execution
   └─ SQLAlchemy ORM
   └─ Transaction management

3. Database → Data Persistence
   └─ Write to persistent volume
   └─ ACID guarantees

4. Database → Backup (Future)
   └─ Scheduled backups
   └─ Point-in-time recovery
```

---

## Security Architecture

### Network Security

**Ingress Security**:
- TLS termination (future)
- Rate limiting (future)
- IP whitelisting (future)

**Service Mesh** (Future):
- mTLS between services
- Service-to-service authentication
- Traffic encryption

**Network Policies** (Future):
- Restrict pod-to-pod communication
- Deny all by default
- Allow specific traffic

### Secret Management

**Current Implementation**:
- Kubernetes Secrets (base64 encoded)
- Environment variable injection
- Secret rotation procedures

**Future Enhancements**:
- External Secrets Operator
- HashiCorp Vault integration
- Sealed Secrets for Git storage
- Automatic secret rotation

### Authentication & Authorization

**Current Implementation**:
- JWT-based authentication
- Secret key from Kubernetes Secret
- Session management

**Future Enhancements**:
- OAuth 2.0 / OpenID Connect
- Role-based access control (RBAC)
- API key management
- Multi-factor authentication

### Container Security

**Image Security**:
- Multi-stage builds (minimal attack surface)
- Non-root user execution
- Vulnerability scanning (future)
- Image signing (future)

**Runtime Security**:
- Read-only root filesystem (future)
- Security contexts
- Pod security policies (future)
- AppArmor/SELinux profiles (future)

---

## Scalability & Performance

### Horizontal Scaling

**Automatic Scaling** (HPA):
- Metrics: CPU utilization, Memory utilization
- Thresholds: CPU > 70%, Memory > 80%
- Scale up: Add pods when threshold exceeded
- Scale down: Remove pods when below threshold
- Cooldown: 5 minutes between scale operations

**Manual Scaling**:
```bash
# Scale frontend to 3 replicas
kubectl scale deployment/frontend --replicas=3 -n todo-app

# Or use helper script
./scripts/scale-service.sh frontend 3
```

### Vertical Scaling

**Resource Requests**:
- Minimum resources guaranteed
- Used for scheduling decisions

**Resource Limits**:
- Maximum resources allowed
- Prevents resource exhaustion

**Right-sizing**:
- Monitor actual usage
- Adjust requests/limits based on metrics
- Use VPA (Vertical Pod Autoscaler) in future

### Performance Optimization

**Frontend**:
- Static asset caching
- Code splitting
- Image optimization
- CDN integration (future)

**Backend**:
- Database connection pooling
- Query optimization
- Caching layer (Redis, future)
- Async processing (Celery, future)

**Database**:
- Indexing strategy
- Query optimization
- Connection pooling
- Read replicas (future)

---

## Monitoring & Observability

### Metrics Collection

**Metrics Server**:
- CPU and memory metrics
- Pod-level metrics
- Node-level metrics

**Prometheus** (Future):
- Application metrics
- Custom metrics
- Alerting rules

### Logging

**Current Implementation**:
- Container logs via kubectl
- Log viewing helper script
- Centralized log access

**Future Enhancements**:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Fluentd for log aggregation
- Structured logging
- Log retention policies

### Tracing

**Future Implementation**:
- Jaeger or Zipkin
- Distributed tracing
- Request correlation
- Performance profiling

### Health Checks

**Liveness Probes**:
- Detect crashed containers
- Automatic restart on failure

**Readiness Probes**:
- Detect when pod is ready
- Remove from service endpoints when not ready

**Health Check Script**:
- 8-category comprehensive check
- Cluster, namespace, deployment, pod, service, application, ingress, resources

---

## Disaster Recovery

### Backup Strategy

**Database Backups** (Future):
- Scheduled backups (daily)
- Point-in-time recovery
- Backup retention (30 days)
- Offsite storage

**Configuration Backups**:
- Helm values in Git
- Kubernetes manifests in Git
- Secret backup procedures

### Recovery Procedures

**Pod Failure**:
- Automatic restart by Kubernetes
- Liveness probe triggers restart
- No manual intervention needed

**Node Failure**:
- Pods rescheduled to healthy nodes
- Automatic by Kubernetes scheduler
- Persistent data preserved

**Cluster Failure**:
- Restore from backup
- Redeploy using Helm
- Restore database from backup

**Data Loss**:
- Restore from database backup
- Point-in-time recovery
- Transaction log replay

---

## Technology Stack

### Frontend

- **Framework**: Next.js 14
- **UI Library**: React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context / Zustand
- **HTTP Client**: Fetch API / Axios

### Backend

- **Framework**: FastAPI
- **Language**: Python 3.11
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Validation**: Pydantic
- **AI Integration**: OpenAI API

### Database

- **RDBMS**: PostgreSQL 15
- **Connection Pooling**: SQLAlchemy
- **Migrations**: Alembic

### Infrastructure

- **Container Runtime**: Docker
- **Orchestration**: Kubernetes (Minikube)
- **Package Manager**: Helm 3
- **Ingress**: NGINX Ingress Controller
- **Metrics**: Metrics Server

### Development Tools

- **Version Control**: Git
- **CI/CD**: GitHub Actions (future)
- **Testing**: pytest, Jest
- **Linting**: ESLint, Pylint
- **Formatting**: Prettier, Black

---

## Design Decisions

### 1. Minikube for Local Development

**Decision**: Use Minikube instead of Docker Desktop Kubernetes or kind

**Rationale**:
- Cross-platform support (Windows, macOS, Linux)
- Easy addon management (Ingress, Metrics Server)
- Isolated environment
- Production-like Kubernetes experience
- Active community support

**Trade-offs**:
- Requires separate installation
- Additional resource overhead
- Not suitable for production

### 2. Helm for Package Management

**Decision**: Use Helm charts instead of raw Kubernetes manifests

**Rationale**:
- Templating and parameterization
- Environment-specific configurations
- Version management
- Rollback capabilities
- Industry standard

**Trade-offs**:
- Additional learning curve
- Template complexity
- Debugging can be harder

### 3. Multi-Stage Docker Builds

**Decision**: Use multi-stage builds for all images

**Rationale**:
- Smaller image sizes
- Faster deployments
- Reduced attack surface
- Separation of build and runtime dependencies

**Trade-offs**:
- Longer build times
- More complex Dockerfiles

### 4. ClusterIP Services

**Decision**: Use ClusterIP for all services, expose via Ingress

**Rationale**:
- Internal-only access
- Single entry point (Ingress)
- Better security
- Standard Kubernetes pattern

**Trade-offs**:
- Requires Ingress controller
- Additional configuration

### 5. Horizontal Pod Autoscaling

**Decision**: Implement HPA for frontend and backend

**Rationale**:
- Automatic scaling based on load
- Resource efficiency
- Cost optimization
- Production-ready pattern

**Trade-offs**:
- Requires Metrics Server
- Scaling delays (cooldown periods)
- Complexity in tuning thresholds

### 6. Single Database Pod

**Decision**: Single PostgreSQL pod (not StatefulSet)

**Rationale**:
- Sufficient for local development
- Simpler configuration
- Easier troubleshooting
- Lower resource usage

**Trade-offs**:
- No high availability
- Single point of failure
- Not production-ready

**Future**: Migrate to StatefulSet with replication for production

### 7. Configuration Profiles

**Decision**: Separate values files for dev/test/prod

**Rationale**:
- Environment-specific configurations
- Easy switching between profiles
- Version-controlled configurations
- Clear separation of concerns

**Trade-offs**:
- Multiple files to maintain
- Potential configuration drift

### 8. Secret Management Helper Scripts

**Decision**: Create interactive scripts for secret management

**Rationale**:
- User-friendly interface
- Reduces errors
- Consistent procedures
- Cross-platform support

**Trade-offs**:
- Additional maintenance
- Not suitable for automation

**Future**: Integrate with external secret managers

---

## Future Enhancements

### Short-term (1-3 months)

1. **Production Profile**: Complete production-ready configuration
2. **Monitoring Stack**: Prometheus + Grafana
3. **Logging Stack**: ELK or Loki
4. **Database HA**: PostgreSQL replication
5. **Backup Automation**: Scheduled database backups

### Medium-term (3-6 months)

1. **Service Mesh**: Istio or Linkerd
2. **GitOps**: ArgoCD or Flux
3. **External Secrets**: Vault or AWS Secrets Manager
4. **Network Policies**: Pod-to-pod communication restrictions
5. **CI/CD Pipeline**: Automated testing and deployment

### Long-term (6-12 months)

1. **Multi-cluster**: Support for multiple Kubernetes clusters
2. **Cloud Migration**: AWS EKS, GCP GKE, or Azure AKS
3. **Advanced Scaling**: Custom metrics, predictive scaling
4. **Chaos Engineering**: Fault injection, resilience testing
5. **Cost Optimization**: Resource right-sizing, spot instances

---

## Conclusion

Phase IV Local Kubernetes Deployment provides a complete, production-like environment for the Todo App with:

✅ **Comprehensive Architecture**: 3-tier microservices with proper separation
✅ **Scalability**: Horizontal and vertical scaling capabilities
✅ **Reliability**: Health checks, rolling updates, automatic restarts
✅ **Security**: Secret management, network isolation, container security
✅ **Observability**: Metrics, logging, health checks
✅ **Maintainability**: Configuration profiles, helper scripts, documentation

The architecture is designed to be:
- **Extensible**: Easy to add new services or features
- **Maintainable**: Clear structure and comprehensive documentation
- **Scalable**: Horizontal and vertical scaling support
- **Secure**: Multiple layers of security controls
- **Observable**: Comprehensive monitoring and logging

---

**Document Version**: 1.0
**Last Updated**: February 7, 2026
**Maintained By**: Phase IV Development Team
**Review Cycle**: Quarterly
