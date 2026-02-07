# Phase IV: Local Kubernetes Deployment

**Status**: 🚧 In Development
**Branch**: `001-local-k8s-deployment`
**Technology Stack**: Docker, Minikube, Kubernetes, Helm

## Overview

Phase IV containerizes the Phase III AI-Powered Todo Chatbot application and deploys it to a local Kubernetes cluster (Minikube). This phase focuses on containerization, orchestration, and operational maturity without changing application business logic.

## Features

- ✅ Docker containerization for all services (frontend, backend, database)
- ✅ Local Kubernetes deployment with Minikube
- ✅ Helm chart-based installation
- ✅ One-command deployment
- ✅ Cross-platform support (Windows, macOS, Linux)
- ✅ Environment reproducibility
- ✅ Service scaling and resource management
- ✅ Health checks and monitoring
- ✅ Configuration management

## Architecture

```
Minikube Cluster
│
├── Namespace: todo-app
│
├── Frontend (Deployment + Service)
│   └── Next.js 14 + TypeScript
│
├── Backend (Deployment + Service)
│   └── FastAPI + Python 3.11
│
├── Database (StatefulSet + Service)
│   └── PostgreSQL 15
│
└── Ingress (NGINX)
    └── http://todo.local
```

## Prerequisites

### Required Software

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| Docker | 24.0+ | Container runtime |
| Minikube | 1.30+ | Local Kubernetes cluster |
| kubectl | 1.28+ | Kubernetes CLI |
| Helm | 3.12+ | Kubernetes package manager |

### System Requirements

- **RAM**: 8GB minimum (12GB recommended)
- **Disk Space**: 20GB free
- **OS**: Windows 10+, macOS 11+, or Ubuntu 20.04+
- **Network**: Internet access for pulling images

## Quick Start

### 1. Validate Prerequisites

```bash
# Linux/macOS
./scripts/validate-prerequisites.sh

# Windows
scripts\validate-prerequisites.bat
```

### 2. Start Minikube

```bash
# Linux/macOS
./scripts/setup-minikube.sh

# Windows
scripts\setup-minikube.bat
```

### 3. Configure Local DNS

Add to your hosts file:
```
<minikube-ip> todo.local
```

### 4. Deploy Application

```bash
# Linux/macOS
./scripts/deploy.sh

# Windows
scripts\deploy.bat
```

### 5. Access Application

Open your browser: http://todo.local

## Directory Structure

```
phase-4-kubernetes/
├── docker/                 # Docker containerization artifacts
│   ├── frontend/          # Frontend Dockerfile and config
│   ├── backend/           # Backend Dockerfile and config
│   └── database/          # Database initialization scripts
├── k8s/                   # Kubernetes manifests
│   ├── frontend/          # Frontend resources
│   ├── backend/           # Backend resources
│   ├── database/          # Database resources
│   └── ingress.yaml       # Ingress configuration
├── helm/                  # Helm chart
│   └── todo-app/         # Main chart
│       ├── Chart.yaml    # Chart metadata
│       ├── values.yaml   # Default values
│       └── templates/    # Kubernetes resource templates
├── scripts/               # Automation scripts
│   ├── setup-minikube.sh # Minikube initialization
│   ├── build-images.sh   # Docker image building
│   ├── deploy.sh         # One-command deployment
│   └── cleanup.sh        # Environment teardown
├── docs/                  # Documentation
│   ├── SETUP.md          # Setup guide
│   ├── DEPLOYMENT.md     # Deployment instructions
│   ├── TROUBLESHOOTING.md # Common issues
│   └── SCALING.md        # Scaling guide
├── tests/                 # Infrastructure tests
├── app/                   # Phase III application code (copied)
│   ├── frontend/         # Next.js application
│   └── backend/          # FastAPI application
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your values
```

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for chatbot
- `SECRET_KEY`: JWT secret key
- `INGRESS_HOST`: Local hostname (default: todo.local)

### Helm Values

Customize deployment via Helm values:

```bash
# Development profile
helm install todo-app ./helm/todo-app -f ./helm/todo-app/values-dev.yaml

# Custom values
helm install todo-app ./helm/todo-app \
  --set frontend.replicaCount=2 \
  --set backend.replicaCount=2
```

## Common Operations

### Scaling Services

```bash
# Scale backend to 3 replicas
kubectl scale deployment backend --replicas=3 -n todo-app

# Or use helper script
./scripts/scale-service.sh backend 3
```

### Viewing Logs

```bash
# Follow backend logs
kubectl logs -f deployment/backend -n todo-app

# Or use helper script
./scripts/view-logs.sh backend
```

### Checking Health

```bash
# Check all pods
kubectl get pods -n todo-app

# Check service endpoints
kubectl get svc -n todo-app

# Or use helper script
./scripts/check-health.sh
```

### Cleanup

```bash
# Uninstall application
helm uninstall todo-app -n todo-app

# Delete namespace
kubectl delete namespace todo-app

# Or use cleanup script
./scripts/cleanup.sh
```

## Documentation

- [Setup Guide](docs/SETUP.md) - Prerequisites and installation
- [Deployment Guide](docs/DEPLOYMENT.md) - Deployment instructions
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [Scaling Guide](docs/SCALING.md) - Service scaling and resource management
- [Architecture](docs/ARCHITECTURE.md) - System architecture overview

## Development

### Building Images

```bash
# Build all images
./scripts/build-images.sh

# Build specific image
docker build -t todo-frontend:latest -f docker/frontend/Dockerfile app/frontend/
```

### Testing Deployment

```bash
# Run deployment test
./tests/deployment-test.sh

# Validate Helm chart
./tests/helm-lint.sh

# Validate Kubernetes manifests
./tests/k8s-validate.sh
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

### Image Pull Errors

```bash
# Verify images in Minikube
eval $(minikube docker-env)
docker images | grep todo

# Rebuild if needed
./scripts/build-images.sh
```

### Ingress Not Working

```bash
# Check Ingress addon
minikube addons list | grep ingress

# Enable if disabled
minikube addons enable ingress

# Verify hosts file
cat /etc/hosts | grep todo.local
```

For more troubleshooting, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Success Criteria

Phase IV is complete when:

- ✅ All services run successfully in Minikube
- ✅ Deployment completes in <10 minutes from clean environment
- ✅ 95%+ first-attempt success rate
- ✅ All services ready within 5 minutes
- ✅ Cross-platform compatibility (Windows, macOS, Linux)
- ✅ Zero data loss during service restarts
- ✅ Health checks detect failures within 10 seconds
- ✅ Scaling operations complete within 1 minute

## Next Phase

**Phase V: Advanced Cloud Deployment**
- Apache Kafka for event streaming
- Dapr for microservices
- DigitalOcean Kubernetes (DOKS)
- Production-grade infrastructure

See [../phase-5-cloud-deployment/README.md](../phase-5-cloud-deployment/README.md) for Phase V details.

## Support

If you encounter issues:
1. Check the [troubleshooting guide](docs/TROUBLESHOOTING.md)
2. Review pod logs and events
3. Verify all prerequisites are met
4. Ensure sufficient system resources

---

**Previous Phase**: [Phase III - AI Chatbot](../phase-3-ai-chatbot/README.md)
**Next Phase**: [Phase V - Cloud Deployment](../phase-5-cloud-deployment/README.md)
