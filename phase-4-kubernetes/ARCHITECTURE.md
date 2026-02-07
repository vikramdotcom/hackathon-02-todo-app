# Phase IV - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Minikube Cluster                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Ingress Controller (NGINX)             │    │
│  │                  todo.local                         │    │
│  └─────────────┬──────────────────────┬────────────────┘    │
│                │                      │                      │
│                │ /                    │ /api                 │
│                ▼                      ▼                      │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │   Frontend Service   │  │   Backend Service    │        │
│  │    ClusterIP:3000    │  │   ClusterIP:8000     │        │
│  └──────────┬───────────┘  └──────────┬───────────┘        │
│             │                          │                     │
│             ▼                          ▼                     │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │  Frontend Deployment │  │  Backend Deployment  │        │
│  │    (Next.js 14)      │  │    (FastAPI)         │        │
│  │    Replicas: 2       │  │    Replicas: 2       │        │
│  │    Port: 3000        │  │    Port: 8000        │        │
│  └──────────────────────┘  └──────────┬───────────┘        │
│                                        │                     │
│                                        │ DATABASE_URL        │
│                                        ▼                     │
│                          ┌──────────────────────┐           │
│                          │  Database Service    │           │
│                          │   ClusterIP:5432     │           │
│                          └──────────┬───────────┘           │
│                                     │                        │
│                                     ▼                        │
│                          ┌──────────────────────┐           │
│                          │ Database Deployment  │           │
│                          │  (PostgreSQL 15)     │           │
│                          │   Replicas: 1        │           │
│                          │   Port: 5432         │           │
│                          └──────────┬───────────┘           │
│                                     │                        │
│                                     ▼                        │
│                          ┌──────────────────────┐           │
│                          │ PersistentVolume     │           │
│                          │    (5Gi storage)     │           │
│                          └──────────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Next.js 14)

**Image:** `todo-frontend:latest`
**Base:** Node.js 18 Alpine
**Build:** Multi-stage (deps → builder → runner)
**Port:** 3000
**Replicas:** 2 (configurable)

**Resources:**
- Requests: 256Mi RAM, 250m CPU
- Limits: 512Mi RAM, 500m CPU

**Health Checks:**
- Liveness: HTTP GET / (30s initial, 10s period)
- Readiness: HTTP GET / (10s initial, 5s period)

**Environment:**
- `NEXT_PUBLIC_API_URL`: API endpoint URL
- `NODE_ENV`: production

### Backend (FastAPI)

**Image:** `todo-backend:latest`
**Base:** Python 3.11 Slim
**Build:** Multi-stage (builder → runner)
**Port:** 8000
**Replicas:** 2 (configurable)

**Resources:**
- Requests: 256Mi RAM, 250m CPU
- Limits: 512Mi RAM, 500m CPU

**Health Checks:**
- Liveness: HTTP GET /health (30s initial, 10s period)
- Readiness: HTTP GET /health (10s initial, 5s period)

**Init Container:**
- Waits for database to be ready using `pg_isready`

**Environment:**
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Application secret key
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `DATABASE_HOST`, `DATABASE_PORT`: Database connection details
- `LOG_LEVEL`, `ENVIRONMENT`: Application settings

**Startup:**
1. Wait for database (init container)
2. Run Alembic migrations (entrypoint)
3. Start Uvicorn server

### Database (PostgreSQL 15)

**Image:** `postgres:15-alpine`
**Port:** 5432
**Replicas:** 1 (stateful)

**Resources:**
- Requests: 256Mi RAM, 250m CPU
- Limits: 512Mi RAM, 500m CPU

**Health Checks:**
- Liveness: `pg_isready -U postgres` (30s initial, 10s period)
- Readiness: `pg_isready -U postgres` (5s initial, 5s period)

**Storage:**
- PersistentVolumeClaim: 5Gi
- StorageClass: standard (Minikube default)
- AccessMode: ReadWriteOnce
- Mount: `/var/lib/postgresql/data`
- PGDATA: `/var/lib/postgresql/data/pgdata`

**Environment:**
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

### Ingress (NGINX)

**Host:** `todo.local`
**Class:** nginx

**Routes:**
- `/api/*` → backend:8000 (with path rewrite)
- `/*` → frontend:3000

**Annotations:**
- `nginx.ingress.kubernetes.io/rewrite-target: /$2`
- `nginx.ingress.kubernetes.io/use-regex: "true"`

## Configuration Management

### ConfigMap (todo-app-config)

Non-sensitive configuration:
- `NEXT_PUBLIC_API_URL`: Frontend API endpoint
- `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`: Database connection
- `LOG_LEVEL`, `ENVIRONMENT`: Application settings

### Secret (todo-app-secrets)

Sensitive data (base64 encoded):
- `POSTGRES_USER`, `POSTGRES_PASSWORD`: Database credentials
- `DATABASE_URL`: Full connection string
- `SECRET_KEY`: Application secret
- `OPENAI_API_KEY`: OpenAI API key (optional)

## Networking

### Service Types

All services use **ClusterIP** (internal only):
- `frontend`: 3000 → frontend pods
- `backend`: 8000 → backend pods
- `database`: 5432 → database pod

External access via **Ingress** only.

### DNS Resolution

Services are accessible within the cluster:
- `frontend.todo-app.svc.cluster.local:3000`
- `backend.todo-app.svc.cluster.local:8000`
- `database.todo-app.svc.cluster.local:5432`

Short names work within the same namespace:
- `frontend:3000`
- `backend:8000`
- `database:5432`

## Storage

### PersistentVolume

- **Provisioner:** Minikube dynamic provisioner
- **StorageClass:** standard
- **Capacity:** 5Gi
- **Access:** ReadWriteOnce
- **Reclaim Policy:** Delete (default)

### Data Persistence

Database data persists across pod restarts but is deleted when:
- PVC is deleted
- Minikube cluster is deleted

For production, use:
- External storage provider
- Regular backups
- Snapshot capabilities

## Security

### Pod Security

- Frontend runs as non-root user (nextjs:1001)
- Backend runs as root (for pg_isready in init container)
- Database runs as postgres user

### Network Policies

Currently **not implemented** (all pods can communicate).

For production, implement:
- Deny all by default
- Allow frontend → backend
- Allow backend → database
- Allow Ingress → frontend/backend

### Secrets Management

Current: Kubernetes Secrets (base64 encoded)

For production, consider:
- External secret managers (Vault, AWS Secrets Manager)
- Sealed Secrets
- SOPS (Secrets OPerationS)

## Resource Management

### Resource Requests

Guaranteed resources:
- Frontend: 256Mi RAM, 250m CPU per pod
- Backend: 256Mi RAM, 250m CPU per pod
- Database: 256Mi RAM, 250m CPU per pod

**Total minimum:** ~768Mi RAM, 750m CPU

### Resource Limits

Maximum resources:
- Frontend: 512Mi RAM, 500m CPU per pod
- Backend: 512Mi RAM, 500m CPU per pod
- Database: 512Mi RAM, 500m CPU per pod

**Total maximum:** ~1.5Gi RAM, 1.5 CPU

### Scaling Considerations

**Horizontal (replicas):**
- Frontend: Can scale freely (stateless)
- Backend: Can scale freely (stateless)
- Database: Single replica (stateful)

**Vertical (resources):**
- Adjust limits in deployment YAML
- Restart deployments to apply

## High Availability

### Current Setup (Development)

- Frontend: 2 replicas (load balanced)
- Backend: 2 replicas (load balanced)
- Database: 1 replica (single point of failure)

### Production Recommendations

1. **Database HA:**
   - PostgreSQL replication (primary + replicas)
   - Or use managed database (RDS, Cloud SQL)

2. **Multi-zone deployment:**
   - Spread pods across availability zones
   - Use pod anti-affinity rules

3. **Backup and Recovery:**
   - Automated database backups
   - Point-in-time recovery
   - Disaster recovery plan

## Monitoring and Observability

### Health Checks

All components have:
- **Liveness probes:** Restart if unhealthy
- **Readiness probes:** Remove from service if not ready

### Metrics (via metrics-server)

Available metrics:
- Pod CPU/memory usage
- Node CPU/memory usage

Access via:
```bash
kubectl top pods -n todo-app
kubectl top nodes
```

### Logging

Logs available via:
```bash
kubectl logs <pod-name> -n todo-app
kubectl logs -f deployment/<name> -n todo-app
```

### Production Monitoring

Recommended additions:
- **Prometheus:** Metrics collection
- **Grafana:** Visualization
- **Loki:** Log aggregation
- **Jaeger:** Distributed tracing
- **AlertManager:** Alerting

## Deployment Strategy

### Current: Rolling Update

Default Kubernetes strategy:
- Max unavailable: 25%
- Max surge: 25%
- Zero-downtime deployments

### Rollback

```bash
# View history
kubectl rollout history deployment/backend -n todo-app

# Rollback to previous
kubectl rollout undo deployment/backend -n todo-app

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n todo-app
```

### Blue-Green / Canary

Not implemented. For production:
- Use Helm for versioned releases
- Implement canary deployments with Flagger
- Use service mesh (Istio, Linkerd) for traffic splitting

## Development Workflow

1. **Code changes** in Phase III
2. **Build images** with `build-images.sh`
3. **Deploy** with `deploy.sh` (applies changes)
4. **Verify** with `status.sh`
5. **Debug** with `kubectl logs` and `kubectl describe`
6. **Iterate** (repeat 1-5)

## CI/CD Integration

For automated deployments:

1. **Build stage:**
   - Build Docker images
   - Tag with commit SHA or version
   - Push to registry

2. **Test stage:**
   - Run unit tests
   - Run integration tests
   - Security scanning

3. **Deploy stage:**
   - Update image tags in YAML
   - Apply Kubernetes manifests
   - Wait for rollout completion
   - Run smoke tests

## Cost Optimization

### Development (Minikube)

- Free (local resources)
- Minimal resource usage
- Stop when not in use

### Production (Cloud)

Optimization strategies:
- Right-size resource requests/limits
- Use node autoscaling
- Use pod autoscaling (HPA)
- Use spot/preemptible instances
- Implement resource quotas
- Monitor and optimize continuously

## Disaster Recovery

### Backup Strategy

**Database:**
- Regular pg_dump backups
- Store in external storage (S3, GCS)
- Test restore procedures

**Configuration:**
- Version control all YAML files
- Store secrets in secret manager
- Document manual steps

### Recovery Procedures

1. **Pod failure:** Automatic (Kubernetes restarts)
2. **Node failure:** Automatic (pods rescheduled)
3. **Cluster failure:** Manual (restore from backups)
4. **Data corruption:** Restore from backup

## Future Enhancements

1. **Helm Charts:** Package management
2. **Service Mesh:** Advanced traffic management
3. **GitOps:** Automated deployments (ArgoCD, Flux)
4. **Observability:** Full monitoring stack
5. **Security:** Network policies, pod security policies
6. **Multi-environment:** Dev, staging, production
7. **Database HA:** Replication and failover
8. **Autoscaling:** HPA and VPA
9. **CI/CD:** Automated pipelines
10. **Infrastructure as Code:** Terraform for cloud resources
