# Phase V Deployment Guide

## Table of Contents

- [Local Development Deployment](#local-development-deployment)
- [Minikube Deployment](#minikube-deployment)
- [DigitalOcean Kubernetes (DOKS) Deployment](#digitalocean-kubernetes-doks-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

## Local Development Deployment

### Prerequisites

- Docker Desktop
- Docker Compose
- Python 3.11+

### Quick Start

```bash
cd phase-5-cloud-deployment/backend

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend

# Access services
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Redpanda Console: http://localhost:8080
```

### Services Included

- **Backend API**: FastAPI application on port 8000
- **PostgreSQL**: Database on port 5432
- **Redpanda**: Kafka-compatible message broker on port 19092
- **Redpanda Console**: Web UI for Kafka on port 8080
- **Dapr Sidecar**: Service mesh on port 3500

## Minikube Deployment

### Prerequisites

- Minikube installed
- kubectl installed
- Dapr CLI installed

### Setup Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster
kubectl cluster-info
```

### Initialize Dapr

```bash
# Initialize Dapr in Kubernetes
dapr init -k

# Verify Dapr installation
dapr status -k

# Open Dapr dashboard
dapr dashboard -k
```

### Deploy Application

```bash
cd phase-5-cloud-deployment

# Apply Dapr components
kubectl apply -f k8s/dapr-components/

# Deploy backend
kubectl apply -f k8s/base/backend/

# Check deployment status
kubectl get pods
kubectl get services

# Get Minikube IP
minikube ip

# Access application
# http://<minikube-ip>:<service-port>
```

### Using Helm

```bash
cd phase-5-cloud-deployment/helm

# Install with Helm
helm install todo-chatbot ./todo-chatbot

# Upgrade deployment
helm upgrade todo-chatbot ./todo-chatbot

# Check status
helm status todo-chatbot

# Uninstall
helm uninstall todo-chatbot
```

## DigitalOcean Kubernetes (DOKS) Deployment

### Prerequisites

- DigitalOcean account
- doctl CLI installed and configured
- kubectl configured for DOKS cluster

### Create DOKS Cluster

```bash
# Create cluster
doctl kubernetes cluster create todo-chatbot-cluster \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3"

# Get cluster credentials
doctl kubernetes cluster kubeconfig save todo-chatbot-cluster

# Verify connection
kubectl get nodes
```

### Setup External Services

#### Neon PostgreSQL

1. Create account at https://neon.tech
2. Create new project: "todo-chatbot-prod"
3. Create database: "todo_db"
4. Copy connection string
5. Update DATABASE_URL in secrets

#### Redpanda Cloud

1. Create account at https://redpanda.com/cloud
2. Create serverless cluster
3. Create topics:
   - task-events
   - reminders
   - task-updates
4. Configure SASL authentication
5. Copy bootstrap servers and credentials

### Configure Secrets

```bash
# Create namespace
kubectl create namespace todo-chatbot

# Create database secret
kubectl create secret generic database-secret \
  --from-literal=url='postgresql://user:pass@host:5432/todo_db' \
  -n todo-chatbot

# Create Kafka secret
kubectl create secret generic kafka-secret \
  --from-literal=bootstrap-servers='your-cluster.redpanda.cloud:9092' \
  --from-literal=sasl-username='your-username' \
  --from-literal=sasl-password='your-password' \
  -n todo-chatbot

# Verify secrets
kubectl get secrets -n todo-chatbot
```

### Deploy with Helm

```bash
cd phase-5-cloud-deployment/helm

# Update values for production
cat > values-production.yaml << EOF
environment: production
replicaCount: 3

image:
  repository: your-registry/todo-backend
  tag: latest
  pullPolicy: Always

database:
  url: "from-secret"

kafka:
  bootstrapServers: "from-secret"

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: api.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: api-tls
      hosts:
        - api.yourdomain.com
EOF

# Install
helm install todo-chatbot ./todo-chatbot \
  -f values-production.yaml \
  -n todo-chatbot

# Check status
kubectl get pods -n todo-chatbot
kubectl get services -n todo-chatbot
kubectl get ingress -n todo-chatbot
```

### Setup TLS with cert-manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Update ingress to use cert-manager
kubectl annotate ingress todo-chatbot \
  cert-manager.io/cluster-issuer=letsencrypt-prod \
  -n todo-chatbot
```

## Environment Configuration

### Development (.env)

```bash
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://todo_user:todo_password@localhost:5432/todo_db
KAFKA_BOOTSTRAP_SERVERS=localhost:19092
```

### Staging (.env.staging)

```bash
ENVIRONMENT=staging
DEBUG=false
DATABASE_URL=postgresql://user:pass@staging-db:5432/todo_db
KAFKA_BOOTSTRAP_SERVERS=staging-kafka:9092
```

### Production (.env.production)

```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@prod-db.neon.tech:5432/todo_db
KAFKA_BOOTSTRAP_SERVERS=prod-cluster.redpanda.cloud:9092
KAFKA_SASL_USERNAME=prod-user
KAFKA_SASL_PASSWORD=prod-password
```

## Database Setup

### Run Migrations

```bash
# Development
make migrate

# Production (via kubectl)
kubectl exec -it deployment/todo-backend -n todo-chatbot -- \
  alembic upgrade head
```

### Seed Data (Development Only)

```bash
# Local
make seed

# Minikube
kubectl exec -it deployment/todo-backend -- \
  python scripts/seed_database.py
```

### Backup Database

```bash
# PostgreSQL backup
pg_dump -h host -U user -d todo_db > backup.sql

# Restore
psql -h host -U user -d todo_db < backup.sql
```

## Monitoring and Logging

### View Logs

```bash
# Local
docker-compose logs -f backend

# Kubernetes
kubectl logs -f deployment/todo-backend -n todo-chatbot

# Follow logs from all pods
kubectl logs -f -l app=todo-backend -n todo-chatbot
```

### Metrics

```bash
# Access metrics endpoint
curl http://localhost:8000/metrics

# Kubernetes port-forward
kubectl port-forward service/todo-backend 8000:8000 -n todo-chatbot
```

### Health Checks

```bash
# Health check
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/ready

# Liveness check
curl http://localhost:8000/live
```

## Troubleshooting

### Common Issues

**Pods not starting:**
```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-chatbot

# Check logs
kubectl logs <pod-name> -n todo-chatbot

# Check events
kubectl get events -n todo-chatbot --sort-by='.lastTimestamp'
```

**Database connection errors:**
```bash
# Test database connection
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql postgresql://user:pass@host:5432/todo_db

# Check secret
kubectl get secret database-secret -n todo-chatbot -o yaml
```

**Kafka connection errors:**
```bash
# Test Kafka connection
kubectl run -it --rm kafka-test --image=confluentinc/cp-kafka:latest --restart=Never -- \
  kafka-console-producer --broker-list <bootstrap-servers> --topic test

# Check Dapr components
kubectl get components -n todo-chatbot
```

### Rollback Deployment

```bash
# Helm rollback
helm rollback todo-chatbot -n todo-chatbot

# Kubernetes rollback
kubectl rollout undo deployment/todo-backend -n todo-chatbot

# Check rollout status
kubectl rollout status deployment/todo-backend -n todo-chatbot
```

### Scale Deployment

```bash
# Scale up
kubectl scale deployment/todo-backend --replicas=5 -n todo-chatbot

# Scale down
kubectl scale deployment/todo-backend --replicas=2 -n todo-chatbot

# Auto-scaling
kubectl autoscale deployment/todo-backend \
  --min=2 --max=10 --cpu-percent=80 \
  -n todo-chatbot
```

## Production Checklist

- [ ] Database backups configured
- [ ] TLS certificates installed
- [ ] Secrets properly configured
- [ ] Resource limits set
- [ ] Health checks configured
- [ ] Monitoring and alerting setup
- [ ] Log aggregation configured
- [ ] Auto-scaling configured
- [ ] Disaster recovery plan documented
- [ ] Security scanning enabled

## Support

For deployment issues:
- Check logs first
- Review Kubernetes events
- Consult documentation
- Open GitHub issue
