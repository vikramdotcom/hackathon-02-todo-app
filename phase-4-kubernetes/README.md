# Phase IV: Local Kubernetes Deployment

**Status**: 🔜 Planned
**Points**: 250
**Due Date**: Jan 4, 2026
**Technology Stack**: Docker, Minikube, Helm, kubectl-ai, kagent

## Overview

Phase IV containerizes the full-stack application and deploys it to a local Kubernetes cluster using Minikube. This phase introduces container orchestration, service mesh, and AI-powered Kubernetes management tools.

## Planned Features

### Containerization
- 🔜 Docker images for all services
- 🔜 Multi-stage builds for optimization
- 🔜 Docker Compose for local development
- 🔜 Container registry integration
- 🔜 Image versioning and tagging
- 🔜 Security scanning and hardening

### Kubernetes Deployment
- 🔜 Minikube local cluster setup
- 🔜 Kubernetes manifests (Deployments, Services, ConfigMaps, Secrets)
- 🔜 Horizontal Pod Autoscaling (HPA)
- 🔜 Resource limits and requests
- 🔜 Health checks (liveness, readiness)
- 🔜 Rolling updates and rollbacks

### Helm Charts
- 🔜 Helm chart for todo application
- 🔜 Parameterized configurations
- 🔜 Environment-specific values
- 🔜 Chart dependencies
- 🔜 Helm hooks for migrations
- 🔜 Chart testing and validation

### kubectl-ai Integration
- 🔜 Natural language Kubernetes commands
- 🔜 AI-powered troubleshooting
- 🔜 Intelligent resource recommendations
- 🔜 Automated debugging assistance
- 🔜 Context-aware kubectl operations

### kagent (Kubernetes Agent)
- 🔜 AI agent for cluster management
- 🔜 Automated deployment workflows
- 🔜 Intelligent scaling decisions
- 🔜 Anomaly detection and alerts
- 🔜 Self-healing capabilities
- 🔜 Cost optimization recommendations

### Observability
- 🔜 Prometheus metrics collection
- 🔜 Grafana dashboards
- 🔜 Centralized logging (EFK stack)
- 🔜 Distributed tracing (Jaeger)
- 🔜 Service mesh (Istio/Linkerd)
- 🔜 Alert management

## Architecture

```
phase-4-kubernetes/
├── docker/
│   ├── frontend/
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   ├── backend/
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   └── chatbot/
│       ├── Dockerfile
│       └── .dockerignore
├── k8s/
│   ├── base/                  # Base Kubernetes manifests
│   │   ├── namespace.yaml
│   │   ├── frontend/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── ingress.yaml
│   │   ├── backend/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── configmap.yaml
│   │   ├── chatbot/
│   │   │   ├── deployment.yaml
│   │   │   └── service.yaml
│   │   └── database/
│   │       ├── statefulset.yaml
│   │       ├── service.yaml
│   │       └── pvc.yaml
│   └── overlays/              # Kustomize overlays
│       ├── dev/
│       ├── staging/
│       └── prod/
├── helm/
│   └── todo-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       ├── values-prod.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── ingress.yaml
│           ├── configmap.yaml
│           ├── secret.yaml
│           └── hpa.yaml
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yaml
│   │   └── rules.yaml
│   ├── grafana/
│   │   └── dashboards/
│   └── alertmanager/
│       └── config.yaml
├── scripts/
│   ├── setup-minikube.sh
│   ├── build-images.sh
│   ├── deploy.sh
│   └── cleanup.sh
├── docker-compose.yml
└── README.md                  # This file
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containerization | Docker | Package applications into containers |
| Orchestration | Kubernetes (Minikube) | Container orchestration and management |
| Package Manager | Helm | Kubernetes application packaging |
| AI CLI | kubectl-ai | Natural language Kubernetes commands |
| AI Agent | kagent | Intelligent cluster management |
| Metrics | Prometheus | Metrics collection and storage |
| Visualization | Grafana | Metrics dashboards and alerts |
| Logging | EFK Stack | Centralized logging (Elasticsearch, Fluentd, Kibana) |
| Tracing | Jaeger | Distributed tracing |
| Service Mesh | Istio/Linkerd | Traffic management and observability |

## Docker Images

### Frontend Image
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]
```

### Backend Image
```dockerfile
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Kubernetes Resources

### Deployment Example
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  namespace: todo-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service Example
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
  namespace: todo-app
spec:
  selector:
    app: todo-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### Ingress Example
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  namespace: todo-app
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: todo.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-frontend
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: todo-backend
            port:
              number: 80
```

## Helm Chart

### Chart.yaml
```yaml
apiVersion: v2
name: todo-app
description: A Helm chart for Todo Application
type: application
version: 1.0.0
appVersion: "1.0.0"
dependencies:
  - name: postgresql
    version: 12.x.x
    repository: https://charts.bitnami.com/bitnami
```

### values.yaml
```yaml
replicaCount: 3

frontend:
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 80

backend:
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 80
  env:
    DATABASE_URL: postgresql://user:pass@db:5432/todos

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: todo.local
      paths:
        - path: /
          pathType: Prefix

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

## kubectl-ai Usage

### Natural Language Commands
```bash
# Deploy application
kubectl-ai "deploy the todo app with 3 replicas"

# Scale deployment
kubectl-ai "scale the backend to 5 pods"

# Troubleshoot issues
kubectl-ai "why is the frontend pod crashing?"

# Check resource usage
kubectl-ai "show me which pods are using the most memory"

# Update configuration
kubectl-ai "update the backend environment variable DATABASE_URL"
```

## kagent Capabilities

### Automated Workflows
```python
# kagent configuration
from kagent import Agent, Workflow

# Define deployment workflow
deploy_workflow = Workflow(
    name="deploy-todo-app",
    steps=[
        "build_docker_images",
        "push_to_registry",
        "apply_k8s_manifests",
        "wait_for_rollout",
        "run_smoke_tests"
    ]
)

# Intelligent scaling
scaling_agent = Agent(
    name="autoscaler",
    triggers=["high_cpu", "high_memory", "increased_traffic"],
    actions=["scale_up", "scale_down"],
    learning_enabled=True
)

# Self-healing
healing_agent = Agent(
    name="healer",
    monitors=["pod_crashes", "failed_health_checks"],
    actions=["restart_pod", "rollback_deployment", "alert_team"]
)
```

## Development Roadmap

### Phase 4.1: Containerization
- [ ] Create Dockerfiles for all services
- [ ] Optimize image sizes
- [ ] Setup Docker Compose
- [ ] Configure multi-stage builds
- [ ] Implement security scanning

### Phase 4.2: Minikube Setup
- [ ] Install and configure Minikube
- [ ] Setup local registry
- [ ] Configure networking
- [ ] Enable required addons
- [ ] Setup ingress controller

### Phase 4.3: Kubernetes Manifests
- [ ] Create Deployments
- [ ] Define Services
- [ ] Configure ConfigMaps and Secrets
- [ ] Setup Ingress rules
- [ ] Implement HPA

### Phase 4.4: Helm Charts
- [ ] Initialize Helm chart
- [ ] Create templates
- [ ] Define values files
- [ ] Add chart dependencies
- [ ] Test chart installation

### Phase 4.5: AI Tools Integration
- [ ] Setup kubectl-ai
- [ ] Configure kagent
- [ ] Create custom workflows
- [ ] Implement monitoring agents
- [ ] Test AI-powered operations

### Phase 4.6: Observability
- [ ] Deploy Prometheus
- [ ] Setup Grafana dashboards
- [ ] Configure logging stack
- [ ] Implement tracing
- [ ] Setup alerting

## Prerequisites

- Docker Desktop or Docker Engine
- Minikube
- kubectl
- Helm 3+
- kubectl-ai
- kagent
- 8GB+ RAM for Minikube

## Getting Started (Coming Soon)

```bash
# Setup Minikube
./scripts/setup-minikube.sh

# Build Docker images
./scripts/build-images.sh

# Deploy with Helm
helm install todo-app ./helm/todo-app -f ./helm/todo-app/values-dev.yaml

# Access application
minikube service todo-frontend --url

# Use kubectl-ai
kubectl-ai "show me all pods in the todo-app namespace"

# Monitor with Grafana
minikube service grafana --url
```

## Useful Commands

```bash
# Minikube
minikube start --cpus=4 --memory=8192
minikube dashboard
minikube tunnel

# Docker
docker build -t todo-frontend:latest ./docker/frontend
docker-compose up -d

# Kubernetes
kubectl get all -n todo-app
kubectl logs -f deployment/todo-backend -n todo-app
kubectl describe pod <pod-name> -n todo-app

# Helm
helm list
helm upgrade todo-app ./helm/todo-app
helm rollback todo-app 1

# kubectl-ai
kubectl-ai "restart all backend pods"
kubectl-ai "show me resource usage for the last hour"
```

## Migration from Phase III

The Phase III application will be containerized:
- Frontend → Docker image + Kubernetes Deployment
- Backend → Docker image + Kubernetes Deployment
- Chatbot → Docker image + Kubernetes Deployment
- Database → StatefulSet with persistent volumes

## Next Phase

**Phase V: Advanced Cloud Deployment**
- Apache Kafka for event streaming
- Dapr for microservices
- DigitalOcean Kubernetes (DOKS)
- Production-grade infrastructure
- Advanced monitoring and observability

See [../phase-5-cloud-deployment/README.md](../phase-5-cloud-deployment/README.md) for Phase V details.

## Status

🔜 **Not Started** - Waiting for Phase III completion and approval.

---

**Previous Phase**: [Phase III - AI Chatbot](../phase-3-ai-chatbot/README.md)
**Next Phase**: [Phase V - Cloud Deployment](../phase-5-cloud-deployment/README.md)
