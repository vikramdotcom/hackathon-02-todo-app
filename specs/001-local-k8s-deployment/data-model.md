# Data Model: Deployment Configuration

**Feature**: 001-local-k8s-deployment
**Date**: 2026-02-07
**Phase**: Phase 1 - Design

## Overview

This document defines the data entities that represent the deployment configuration and runtime state for the Phase IV Local Kubernetes Deployment. These entities are infrastructure-level (not application data) and describe how services are deployed, configured, and managed in Kubernetes.

---

## Entity 1: Deployment Configuration

### Description
Represents the complete specification of how services should be deployed to Kubernetes, including replica counts, resource limits, environment variables, and service dependencies.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | string | Yes | Kubernetes namespace for all resources (default: "todo-app") |
| `imageRegistry` | string | Yes | Container registry URL (default: "docker.io") |
| `imagePullPolicy` | enum | Yes | When to pull images: Always, IfNotPresent, Never |
| `services` | ServiceConfig[] | Yes | Array of service configurations (frontend, backend, database) |
| `ingress` | IngressConfig | Yes | Ingress configuration for external access |
| `persistence` | PersistenceConfig | Yes | Persistent volume configuration |

### ServiceConfig Sub-Entity

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Service name (frontend, backend, database) |
| `replicaCount` | integer | Yes | Number of pod replicas (1-10) |
| `image.repository` | string | Yes | Container image repository |
| `image.tag` | string | Yes | Container image tag (version) |
| `service.type` | enum | Yes | Service type: ClusterIP, NodePort, LoadBalancer |
| `service.port` | integer | Yes | Service port number |
| `resources.requests.memory` | string | Yes | Minimum memory (e.g., "256Mi") |
| `resources.requests.cpu` | string | Yes | Minimum CPU (e.g., "250m") |
| `resources.limits.memory` | string | Yes | Maximum memory (e.g., "512Mi") |
| `resources.limits.cpu` | string | Yes | Maximum CPU (e.g., "500m") |
| `env` | map[string]string | No | Environment variables |
| `secrets` | map[string]string | No | Secret references |

### IngressConfig Sub-Entity

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `enabled` | boolean | Yes | Whether to create Ingress resource |
| `className` | string | Yes | Ingress class (nginx, traefik, etc.) |
| `host` | string | Yes | Hostname for Ingress (e.g., "todo.local") |
| `tls.enabled` | boolean | No | Whether to enable TLS/SSL |
| `tls.secretName` | string | No | Secret containing TLS certificate |

### PersistenceConfig Sub-Entity

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `enabled` | boolean | Yes | Whether to use persistent storage |
| `size` | string | Yes | Storage size (e.g., "10Gi") |
| `storageClass` | string | Yes | StorageClass name (e.g., "standard") |
| `accessMode` | enum | Yes | Access mode: ReadWriteOnce, ReadWriteMany |

### Validation Rules

- `replicaCount`: Must be between 1 and 10
- `service.port`: Must be between 1 and 65535
- `resources.requests`: Must be less than or equal to `resources.limits`
- `image.tag`: Must not be empty or "latest" in production
- `namespace`: Must match Kubernetes naming conventions (lowercase, alphanumeric, hyphens)

### Example (Helm values.yaml)

```yaml
global:
  namespace: todo-app
  imageRegistry: docker.io
  imagePullPolicy: IfNotPresent

frontend:
  replicaCount: 2
  image:
    repository: todo-frontend
    tag: "1.0.0"
  service:
    type: ClusterIP
    port: 3000
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

backend:
  replicaCount: 2
  image:
    repository: todo-backend
    tag: "1.0.0"
  service:
    type: ClusterIP
    port: 8000
  env:
    DATABASE_URL: "postgresql://user:pass@database:5432/todos"
    OPENAI_MODEL: "gpt-3.5-turbo"
  secrets:
    OPENAI_API_KEY: "backend-secrets/openai-api-key"
    SECRET_KEY: "backend-secrets/jwt-secret"
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

database:
  enabled: true
  replicaCount: 1
  image:
    repository: postgres
    tag: "15-alpine"
  service:
    type: ClusterIP
    port: 5432
  secrets:
    POSTGRES_PASSWORD: "database-secrets/password"
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "500m"

ingress:
  enabled: true
  className: nginx
  host: todo.local
  tls:
    enabled: false

persistence:
  enabled: true
  size: 10Gi
  storageClass: standard
  accessMode: ReadWriteOnce
```

---

## Entity 2: Service Instance

### Description
Represents a running instance of a service (pod) in Kubernetes with its current state, health status, and resource consumption.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Pod name (generated by Kubernetes) |
| `namespace` | string | Yes | Kubernetes namespace |
| `serviceName` | string | Yes | Parent service name (frontend, backend, database) |
| `status` | enum | Yes | Pod status: Pending, Running, Succeeded, Failed, Unknown |
| `phase` | enum | Yes | Pod phase: Pending, Running, Succeeded, Failed, Unknown |
| `ready` | boolean | Yes | Whether pod is ready to serve traffic |
| `restartCount` | integer | Yes | Number of container restarts |
| `startTime` | timestamp | Yes | When pod was started |
| `containerStatuses` | ContainerStatus[] | Yes | Status of each container in pod |
| `resourceUsage` | ResourceUsage | No | Current resource consumption |
| `nodeIP` | string | Yes | IP address of node running pod |
| `podIP` | string | Yes | IP address of pod |

### ContainerStatus Sub-Entity

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Container name |
| `ready` | boolean | Yes | Whether container is ready |
| `restartCount` | integer | Yes | Number of restarts |
| `state` | enum | Yes | Container state: Waiting, Running, Terminated |
| `lastState` | enum | No | Previous container state |

### ResourceUsage Sub-Entity

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `cpuUsage` | string | Yes | Current CPU usage (e.g., "250m") |
| `memoryUsage` | string | Yes | Current memory usage (e.g., "256Mi") |
| `cpuPercentage` | float | Yes | CPU usage as percentage of limit |
| `memoryPercentage` | float | Yes | Memory usage as percentage of limit |

### State Transitions

```
Pending → Running → Succeeded/Failed
         ↓
      Terminated (if failed) → Pending (if restarted)
```

### Example (kubectl get pod output)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: backend-7d8f9c5b6-xk2lm
  namespace: todo-app
  labels:
    app: backend
spec:
  containers:
  - name: backend
    image: todo-backend:1.0.0
status:
  phase: Running
  conditions:
  - type: Ready
    status: "True"
  containerStatuses:
  - name: backend
    ready: true
    restartCount: 0
    state:
      running:
        startedAt: "2026-02-07T10:00:00Z"
  podIP: 172.17.0.5
  hostIP: 192.168.49.2
```

---

## Entity 3: Health Check

### Description
Represents a validation mechanism that determines whether a service is ready to accept traffic and functioning correctly.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | enum | Yes | Probe type: Liveness, Readiness, Startup |
| `handler` | enum | Yes | Handler type: HTTP, TCP, Exec |
| `httpGet.path` | string | Conditional | HTTP endpoint path (required if handler=HTTP) |
| `httpGet.port` | integer | Conditional | HTTP port (required if handler=HTTP) |
| `httpGet.scheme` | enum | No | HTTP or HTTPS (default: HTTP) |
| `exec.command` | string[] | Conditional | Command to execute (required if handler=Exec) |
| `tcpSocket.port` | integer | Conditional | TCP port (required if handler=TCP) |
| `initialDelaySeconds` | integer | Yes | Delay before first probe (default: 0) |
| `periodSeconds` | integer | Yes | How often to probe (default: 10) |
| `timeoutSeconds` | integer | Yes | Probe timeout (default: 1) |
| `successThreshold` | integer | Yes | Consecutive successes to mark healthy (default: 1) |
| `failureThreshold` | integer | Yes | Consecutive failures to mark unhealthy (default: 3) |

### Probe Types

**Liveness Probe**:
- Purpose: Detect deadlocks, infinite loops, or unrecoverable errors
- Action on failure: Restart container
- Use case: Application is running but not responding

**Readiness Probe**:
- Purpose: Detect temporary unavailability (e.g., loading data, warming up)
- Action on failure: Remove pod from service endpoints
- Use case: Application is starting up or temporarily overloaded

**Startup Probe**:
- Purpose: Detect slow-starting applications
- Action on failure: Restart container (after failureThreshold)
- Use case: Application takes >30s to start

### Validation Rules

- `initialDelaySeconds`: Must be ≥ 0
- `periodSeconds`: Must be > 0
- `timeoutSeconds`: Must be > 0 and < periodSeconds
- `successThreshold`: Must be ≥ 1
- `failureThreshold`: Must be ≥ 1
- Liveness probe `initialDelaySeconds` should be > Readiness probe `initialDelaySeconds`

### Example (Backend Liveness Probe)

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
    scheme: HTTP
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3
```

### Example (Database Readiness Probe)

```yaml
readinessProbe:
  exec:
    command:
    - pg_isready
    - -U
    - postgres
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  successThreshold: 1
  failureThreshold: 2
```

---

## Entity 4: Configuration Profile

### Description
Represents a set of environment-specific configuration values that can be applied to a deployment (development, testing, production).

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Profile name (dev, test, prod) |
| `environment` | enum | Yes | Environment type: development, testing, production |
| `overrides` | map[string]any | Yes | Values to override from base configuration |
| `secrets` | SecretReference[] | Yes | References to Kubernetes Secrets |
| `configMaps` | ConfigMapReference[] | Yes | References to Kubernetes ConfigMaps |

### SecretReference Sub-Entity

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Secret name in Kubernetes |
| `key` | string | Yes | Key within secret |
| `envVar` | string | Yes | Environment variable name to inject |

### ConfigMapReference Sub-Entity

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | ConfigMap name in Kubernetes |
| `key` | string | Yes | Key within ConfigMap |
| `envVar` | string | Yes | Environment variable name to inject |

### Example (values-dev.yaml)

```yaml
# Development profile overrides
environment: development

frontend:
  replicaCount: 1
  image:
    tag: "dev"
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "250m"

backend:
  replicaCount: 1
  image:
    tag: "dev"
  env:
    ENVIRONMENT: "development"
    LOG_LEVEL: "DEBUG"
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

database:
  persistence:
    size: 5Gi

ingress:
  host: todo-dev.local
```

### Example (values-test.yaml)

```yaml
# Testing profile overrides
environment: testing

frontend:
  replicaCount: 2
  image:
    tag: "test"

backend:
  replicaCount: 2
  image:
    tag: "test"
  env:
    ENVIRONMENT: "testing"
    LOG_LEVEL: "INFO"

database:
  persistence:
    size: 10Gi

ingress:
  host: todo-test.local
```

---

## Entity 5: Deployment Artifact

### Description
Represents a versioned, immutable package containing all necessary files and configurations for deployment.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `version` | string | Yes | Semantic version (e.g., "1.0.0") |
| `createdAt` | timestamp | Yes | When artifact was created |
| `images` | ImageArtifact[] | Yes | Container images |
| `manifests` | ManifestArtifact[] | Yes | Kubernetes manifests |
| `helmChart` | HelmChartArtifact | Yes | Helm chart package |
| `checksum` | string | Yes | SHA256 checksum for integrity |

### ImageArtifact Sub-Entity

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Image name (frontend, backend, database) |
| `repository` | string | Yes | Full repository path |
| `tag` | string | Yes | Image tag (version) |
| `digest` | string | Yes | SHA256 digest for immutability |
| `size` | integer | Yes | Image size in bytes |
| `createdAt` | timestamp | Yes | When image was built |

### ManifestArtifact Sub-Entity

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `filename` | string | Yes | Manifest filename |
| `kind` | string | Yes | Kubernetes resource kind |
| `apiVersion` | string | Yes | Kubernetes API version |
| `checksum` | string | Yes | SHA256 checksum |

### HelmChartArtifact Sub-Entity

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Chart name (todo-app) |
| `version` | string | Yes | Chart version |
| `appVersion` | string | Yes | Application version |
| `packagePath` | string | Yes | Path to .tgz package |
| `checksum` | string | Yes | SHA256 checksum |

### Example

```yaml
version: "1.0.0"
createdAt: "2026-02-07T10:00:00Z"
images:
  - name: frontend
    repository: docker.io/todo-frontend
    tag: "1.0.0"
    digest: "sha256:abc123..."
    size: 150000000
    createdAt: "2026-02-07T09:30:00Z"
  - name: backend
    repository: docker.io/todo-backend
    tag: "1.0.0"
    digest: "sha256:def456..."
    size: 200000000
    createdAt: "2026-02-07T09:45:00Z"
manifests:
  - filename: namespace.yaml
    kind: Namespace
    apiVersion: v1
    checksum: "sha256:ghi789..."
  - filename: frontend-deployment.yaml
    kind: Deployment
    apiVersion: apps/v1
    checksum: "sha256:jkl012..."
helmChart:
  name: todo-app
  version: "1.0.0"
  appVersion: "1.0.0"
  packagePath: ./helm/todo-app-1.0.0.tgz
  checksum: "sha256:mno345..."
```

---

## Entity Relationships

```
Deployment Configuration (1)
  ├── contains → Service Config (N)
  ├── contains → Ingress Config (1)
  └── contains → Persistence Config (1)

Service Config (1)
  └── creates → Service Instance (N)

Service Instance (1)
  ├── has → Container Status (N)
  ├── has → Resource Usage (1)
  └── monitored by → Health Check (N)

Health Check (N)
  └── validates → Service Instance (1)

Configuration Profile (1)
  ├── overrides → Deployment Configuration (1)
  ├── references → Secret Reference (N)
  └── references → ConfigMap Reference (N)

Deployment Artifact (1)
  ├── contains → Image Artifact (N)
  ├── contains → Manifest Artifact (N)
  └── contains → Helm Chart Artifact (1)
```

---

## Summary

This data model defines 5 core entities for Phase IV deployment:

1. **Deployment Configuration**: How services should be deployed (Helm values)
2. **Service Instance**: Running pods with current state and health
3. **Health Check**: Validation mechanisms for service health
4. **Configuration Profile**: Environment-specific overrides (dev/test/prod)
5. **Deployment Artifact**: Versioned, immutable deployment packages

These entities enable:
- Declarative infrastructure configuration
- Environment-specific customization
- Health monitoring and automatic recovery
- Reproducible deployments
- Version tracking and rollback capability
