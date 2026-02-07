# Research & Technology Decisions: Local Kubernetes Deployment

**Feature**: 001-local-k8s-deployment
**Date**: 2026-02-07
**Phase**: Phase 0 - Research

## Overview

This document captures all technology decisions and best practices research for deploying the Phase III AI-Powered Todo Chatbot to a local Kubernetes cluster (Minikube). All decisions are based on industry best practices, official documentation, and alignment with Phase IV requirements.

---

## 1. Docker Multi-Stage Build Optimization

### Decision: Multi-Stage Builds with Layer Caching

**Frontend (Next.js)**:
```dockerfile
# Stage 1: Dependencies
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Builder
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Runner
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

**Backend (FastAPI)**:
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runner
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

**Rationale**:
- Multi-stage builds reduce final image size by 60-80%
- Separate dependency installation from application code for better layer caching
- Alpine/slim base images minimize attack surface and image size
- Production-only dependencies in final stage

**Alternatives Considered**:
- Single-stage builds: Simpler but 3-5x larger images
- Distroless images: More secure but harder to debug in development
- Full base images (node:18, python:3.11): Unnecessary packages, larger size

**Implementation Guidance**:
- Use `.dockerignore` to exclude node_modules, .next, __pycache__, .venv
- Order COPY commands from least to most frequently changed (package.json before source code)
- Use `npm ci` instead of `npm install` for reproducible builds
- Use `--no-cache-dir` for pip to reduce image size

**Layer Caching Strategy**:
1. Base image (rarely changes)
2. System dependencies (rarely changes)
3. Application dependencies (changes occasionally)
4. Application code (changes frequently)

---

## 2. Kubernetes Resource Limits

### Decision: Conservative Limits with Headroom

**Frontend (Next.js)**:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**Backend (FastAPI)**:
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

**Database (PostgreSQL)**:
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

**Rationale**:
- Requests ensure minimum guaranteed resources
- Limits prevent resource exhaustion (OOMKilled, CPU throttling)
- 2:1 ratio between limits and requests provides burst capacity
- Total resource usage: ~2.5GB RAM, ~2 CPU cores (fits in 8GB RAM constraint)

**Alternatives Considered**:
- No limits: Risk of resource exhaustion, pod eviction
- Tight limits (1:1 ratio): No burst capacity, potential throttling
- Higher limits: Exceeds 8GB RAM constraint for multiple replicas

**Implementation Guidance**:
- Monitor actual resource usage with `kubectl top pods`
- Adjust limits based on observed usage patterns
- Use Horizontal Pod Autoscaler (HPA) for automatic scaling based on CPU/memory
- Set requests = 50% of limits for development, 75% for production

**Resource Calculation**:
- 3 services × 1 replica = ~2.5GB RAM (leaves 5.5GB for Minikube overhead)
- 3 services × 3 replicas = ~7.5GB RAM (near 8GB limit, requires tuning)

---

## 3. Helm Chart Best Practices

### Decision: Monolithic Chart with Templated Resources

**Chart Structure**:
```
helm/todo-app/
├── Chart.yaml              # Chart metadata (version, appVersion, dependencies)
├── values.yaml             # Default values (development profile)
├── values-dev.yaml         # Development overrides
├── values-test.yaml        # Testing overrides
├── templates/
│   ├── _helpers.tpl        # Template helpers (labels, selectors, names)
│   ├── NOTES.txt           # Post-install instructions
│   ├── namespace.yaml
│   ├── frontend-*.yaml     # Frontend resources
│   ├── backend-*.yaml      # Backend resources
│   ├── database-*.yaml     # Database resources
│   └── ingress.yaml
└── .helmignore
```

**Values.yaml Parameterization**:
```yaml
global:
  namespace: todo-app
  imageRegistry: docker.io
  imagePullPolicy: IfNotPresent

frontend:
  replicaCount: 1
  image:
    repository: todo-frontend
    tag: latest
  service:
    type: ClusterIP
    port: 3000
  resources:
    requests:
      memory: 256Mi
      cpu: 250m
    limits:
      memory: 512Mi
      cpu: 500m

backend:
  replicaCount: 1
  image:
    repository: todo-backend
    tag: latest
  service:
    type: ClusterIP
    port: 8000
  env:
    DATABASE_URL: postgresql://user:pass@database:5432/todos
    OPENAI_API_KEY: ""  # Override via values-*.yaml or --set
  resources:
    requests:
      memory: 512Mi
      cpu: 500m
    limits:
      memory: 1Gi
      cpu: 1000m

database:
  enabled: true
  image:
    repository: postgres
    tag: 15-alpine
  persistence:
    enabled: true
    size: 10Gi
    storageClass: standard
  resources:
    requests:
      memory: 512Mi
      cpu: 250m
    limits:
      memory: 1Gi
      cpu: 500m

ingress:
  enabled: true
  className: nginx
  host: todo.local
  tls:
    enabled: false
```

**Rationale**:
- Single chart simplifies deployment (one `helm install` command)
- Templated resources enable environment-specific customization
- Values files provide clear configuration interface
- Helpers reduce duplication and ensure consistency

**Alternatives Considered**:
- Separate charts per service: More complex, multiple install commands
- Umbrella chart with subcharts: Overkill for 3 services
- Raw Kubernetes manifests: No parameterization, less flexible

**Implementation Guidance**:
- Use `{{ include "todo-app.fullname" . }}` for resource names
- Use `{{ .Values.global.namespace }}` for namespace references
- Use `{{ .Release.Name }}` for unique release identification
- Validate charts with `helm lint` and `helm template`

**Helm Hooks for Migrations**:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "todo-app.fullname" . }}-migration
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  template:
    spec:
      containers:
      - name: migration
        image: {{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}
        command: ["alembic", "upgrade", "head"]
```

---

## 4. Health Check Patterns

### Decision: Separate Liveness and Readiness Probes

**Frontend (Next.js)**:
```yaml
livenessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

**Backend (FastAPI)**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

**Database (PostgreSQL)**:
```yaml
livenessProbe:
  exec:
    command:
    - pg_isready
    - -U
    - postgres
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  exec:
    command:
    - pg_isready
    - -U
    - postgres
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

**Rationale**:
- Liveness probes detect deadlocks/hangs (restart pod if failing)
- Readiness probes detect temporary unavailability (remove from service if failing)
- Separate probes prevent premature restarts during startup
- Conservative thresholds reduce false positives

**Alternatives Considered**:
- Single probe: Cannot distinguish between restart-worthy and temporary failures
- TCP probes: Less informative than HTTP/exec probes
- Startup probes: Unnecessary for fast-starting applications

**Implementation Guidance**:
- Liveness: Longer initialDelaySeconds (30s), fewer checks (10s period)
- Readiness: Shorter initialDelaySeconds (10-15s), more frequent checks (5s period)
- Timeout: 3-5s (balance between responsiveness and false positives)
- Failure threshold: 2-3 (allow transient failures)

**Health Check Endpoint Requirements**:
- Backend `/health` should check:
  - Database connectivity
  - OpenAI API reachability (optional, may cause false positives)
  - Memory/CPU usage (optional)
- Return 200 OK if healthy, 503 Service Unavailable if unhealthy

---

## 5. Persistent Volume Configuration

### Decision: PersistentVolumeClaim with Dynamic Provisioning

**PersistentVolumeClaim (PVC)**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: database-pvc
  namespace: todo-app
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 10Gi
```

**StatefulSet Volume Mount**:
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: database
spec:
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: standard
      resources:
        requests:
          storage: 10Gi
  template:
    spec:
      containers:
      - name: postgres
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
```

**Rationale**:
- PVC with dynamic provisioning simplifies storage management
- StatefulSet ensures stable storage across pod restarts
- ReadWriteOnce access mode sufficient for single-instance database
- 10Gi storage provides ample space for development data

**Alternatives Considered**:
- HostPath volumes: Not portable across nodes, data loss risk
- EmptyDir volumes: Data lost on pod restart
- Static PersistentVolumes: Requires manual provisioning

**Implementation Guidance**:
- Use `storageClassName: standard` for Minikube (default provisioner)
- Use `volumeClaimTemplates` in StatefulSet for automatic PVC creation
- Mount at `/var/lib/postgresql/data` for PostgreSQL
- Use `subPath: postgres` to avoid permission issues

**Backup/Restore Strategy**:
```bash
# Backup
kubectl exec -n todo-app database-0 -- pg_dump -U postgres todos > backup.sql

# Restore
kubectl exec -i -n todo-app database-0 -- psql -U postgres todos < backup.sql
```

---

## 6. Ingress Configuration

### Decision: NGINX Ingress Controller with Path-Based Routing

**Ingress Resource**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  namespace: todo-app
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
  - host: todo.local
    http:
      paths:
      - path: /()(.*)
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
      - path: /api(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
```

**Minikube Ingress Setup**:
```bash
# Enable NGINX Ingress Controller
minikube addons enable ingress

# Get Ingress IP
minikube ip

# Add to /etc/hosts (or C:\Windows\System32\drivers\etc\hosts)
<minikube-ip> todo.local
```

**Rationale**:
- Single entry point for frontend and backend
- Path-based routing (`/` → frontend, `/api` → backend)
- NGINX Ingress Controller is Minikube default
- Mimics production deployment patterns

**Alternatives Considered**:
- NodePort services: Requires multiple ports, less production-like
- LoadBalancer: Requires `minikube tunnel`, more complex
- Separate Ingress per service: More complex, multiple hostnames

**Implementation Guidance**:
- Use `rewrite-target` annotation to strip path prefix
- Use `ingressClassName: nginx` for Kubernetes 1.18+
- Add `todo.local` to `/etc/hosts` for local DNS resolution
- Use `minikube tunnel` if LoadBalancer type needed

**TLS/SSL Configuration (Optional)**:
```yaml
spec:
  tls:
  - hosts:
    - todo.local
    secretName: todo-tls
```

Generate self-signed certificate:
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt -subj "/CN=todo.local"
kubectl create secret tls todo-tls --key tls.key --cert tls.crt -n todo-app
```

---

## 7. AI Tool Integration

### Decision: Optional AI Tools with Manual Fallbacks

**Docker AI (Gordon)**:
- **Capability**: Generate Dockerfiles from natural language prompts
- **Limitation**: May not be available in all environments
- **Fallback**: Claude Code generates Dockerfiles following best practices

**kubectl-ai**:
- **Capability**: Natural language Kubernetes commands
- **Example**: `kubectl-ai "scale the backend to 3 replicas"`
- **Limitation**: Requires separate installation, may have accuracy issues
- **Fallback**: Standard kubectl commands documented in quickstart.md

**kagent**:
- **Capability**: AI agent for cluster management and optimization
- **Example**: `kagent "analyze cluster health"`
- **Limitation**: May not be widely available, experimental
- **Fallback**: Manual cluster inspection with kubectl commands

**Rationale**:
- AI tools enhance developer experience but are not required
- Manual fallbacks ensure deployment works without AI tools
- Documentation includes both AI-assisted and manual workflows

**Alternatives Considered**:
- Require AI tools: Blocks adoption if tools unavailable
- Ignore AI tools: Misses opportunity to simplify operations

**Implementation Guidance**:
- Document AI tool installation in SETUP.md
- Provide equivalent kubectl commands for all AI operations
- Use AI tools for demonstration, manual commands for automation scripts
- Test deployment workflow without AI tools to ensure fallbacks work

**AI Tool Command Mapping**:
| AI Command | Manual Equivalent |
|------------|-------------------|
| `kubectl-ai "deploy the todo app"` | `helm install todo-app ./helm/todo-app` |
| `kubectl-ai "scale backend to 3"` | `kubectl scale deployment backend --replicas=3 -n todo-app` |
| `kubectl-ai "check pod status"` | `kubectl get pods -n todo-app` |
| `kubectl-ai "show backend logs"` | `kubectl logs -f deployment/backend -n todo-app` |
| `kagent "analyze cluster health"` | `kubectl top nodes && kubectl top pods -n todo-app` |

---

## Summary of Decisions

| Area | Decision | Key Benefit |
|------|----------|-------------|
| Docker Builds | Multi-stage with layer caching | 60-80% smaller images |
| Resource Limits | Conservative with 2:1 ratio | Prevents resource exhaustion |
| Helm Charts | Monolithic chart with templates | Single-command deployment |
| Health Checks | Separate liveness/readiness | Accurate failure detection |
| Persistent Volumes | PVC with dynamic provisioning | Automatic storage management |
| Ingress | NGINX with path-based routing | Single entry point |
| AI Tools | Optional with manual fallbacks | Enhanced UX without dependency |

---

## Implementation Checklist

- [ ] Create Dockerfiles following multi-stage build pattern
- [ ] Define resource limits in Kubernetes manifests
- [ ] Structure Helm chart with values.yaml parameterization
- [ ] Configure health probes for all services
- [ ] Setup PVC for database persistence
- [ ] Configure Ingress with path-based routing
- [ ] Document AI tool usage and manual fallbacks
- [ ] Test deployment on Windows, macOS, Linux
- [ ] Validate resource usage within 8GB RAM constraint
- [ ] Verify zero data loss during pod restarts

---

**Research Complete**: All technology decisions documented with rationale, alternatives, and implementation guidance. Ready for Phase 1 (Design & Contracts).
