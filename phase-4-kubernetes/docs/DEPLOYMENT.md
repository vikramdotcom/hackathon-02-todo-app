# Phase IV - Deployment Guide

Complete deployment guide for the Todo App on local Kubernetes cluster.

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Methods](#deployment-methods)
4. [Post-Deployment Verification](#post-deployment-verification)
5. [Configuration Management](#configuration-management)
6. [Scaling and Updates](#scaling-and-updates)
7. [Rollback Procedures](#rollback-procedures)
8. [Troubleshooting](#troubleshooting)

---

## Deployment Overview

### Deployment Options

| Method | Use Case | Complexity | Flexibility |
|--------|----------|------------|-------------|
| **Direct kubectl** | Quick testing, simple deployments | Low | Low |
| **Helm Chart** | Production, multiple environments | Medium | High |
| **Automated Scripts** | CI/CD, reproducible deployments | Low | Medium |

### Architecture

```
┌─────────────────────────────────────────┐
│         Minikube Cluster                │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Ingress (todo.local)           │  │
│  └────────┬─────────────────┬───────┘  │
│           │                 │           │
│           ▼                 ▼           │
│  ┌─────────────┐   ┌─────────────┐    │
│  │  Frontend   │   │   Backend   │    │
│  │  (2 pods)   │   │  (2 pods)   │    │
│  └─────────────┘   └──────┬──────┘    │
│                            │            │
│                            ▼            │
│                   ┌─────────────┐      │
│                   │  Database   │      │
│                   │  (1 pod)    │      │
│                   └─────────────┘      │
└─────────────────────────────────────────┘
```

---

## Pre-Deployment Checklist

### 1. Prerequisites Validation

Run the validation script:

**Linux/macOS:**
```bash
./scripts/validate-prerequisites.sh
```

**Windows:**
```cmd
scripts\validate-prerequisites.bat
```

Expected output:
```
✓ Docker installed
✓ Minikube installed
✓ kubectl installed
✓ Helm installed
✓ Docker daemon running
```

### 2. Minikube Cluster

Ensure Minikube is running:
```bash
minikube status
```

If not running, start it:
```bash
./scripts/setup-minikube.sh  # Linux/macOS
scripts\setup-minikube.bat   # Windows
```

### 3. Docker Images

Build the images:
```bash
./scripts/build-images.sh  # Linux/macOS
scripts\build-images.bat   # Windows
```

Verify images exist:
```bash
eval $(minikube docker-env)  # Configure Docker
docker images | grep todo-
```

### 4. Hosts File

Add Minikube IP to hosts file:
```bash
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts  # Linux/macOS
```

Windows (Run as Administrator):
```powershell
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "$(minikube ip) todo.local"
```

### 5. Secrets Configuration

Create secrets file from example:
```bash
cp k8s/secret.yaml.example k8s/secret.yaml
```

Edit `k8s/secret.yaml` with your values:
- Change `POSTGRES_PASSWORD`
- Change `SECRET_KEY`
- Add `OPENAI_API_KEY` (optional)

---

## Deployment Methods

### Method 1: Automated Script Deployment (Recommended for First-Time)

This method uses the automated deployment script that handles all steps.

**Linux/macOS:**
```bash
./scripts/deploy.sh
```

**Windows:**
```cmd
scripts\deploy.bat
```

**What it does:**
1. Validates Minikube is running
2. Checks Docker images exist
3. Creates namespace
4. Creates/verifies secrets
5. Applies ConfigMap
6. Creates PersistentVolumeClaim
7. Deploys database
8. Deploys backend
9. Deploys frontend
10. Configures Ingress
11. Waits for all pods to be ready

**Expected time:** 3-5 minutes

**Output:**
```
✓ Minikube is running
✓ Docker images found
✓ Namespace created
✓ Secrets created
✓ ConfigMap applied
✓ PVC created
✓ Database deployed
✓ Database is ready
✓ Backend deployed
✓ Backend is ready
✓ Frontend deployed
✓ Frontend is ready
✓ Ingress applied
✓ Deployment complete!
```

---

### Method 2: Helm Chart Deployment (Recommended for Production)

This method uses Helm for more flexible, parameterized deployments.

#### Basic Helm Deployment

```bash
./scripts/helm-deploy.sh  # Linux/macOS
scripts\helm-deploy.bat   # Windows
```

Or manually:
```bash
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --wait \
  --timeout 5m
```

#### Development Environment

Use development values:
```bash
helm install todo-app ./helm/todo-app \
  -n todo-app \
  --create-namespace \
  -f helm/todo-app/values-dev.yaml
```

Features:
- Single replica per service
- Reduced resource limits
- Debug logging
- Smaller storage (2Gi)

#### Testing Environment

Use testing values:
```bash
helm install todo-app ./helm/todo-app \
  -n todo-app \
  --create-namespace \
  -f helm/todo-app/values-test.yaml
```

Features:
- Multiple replicas (2 per service)
- Standard resource limits
- Info logging
- Pod disruption budgets enabled

#### Custom Configuration

Override specific values:
```bash
helm install todo-app ./helm/todo-app \
  -n todo-app \
  --create-namespace \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=3 \
  --set secrets.openaiApiKey="sk-..."
```

#### With Version Tags

Deploy specific image versions:
```bash
# Build with version
./scripts/build-images.sh v1.0.0

# Deploy with version
helm install todo-app ./helm/todo-app \
  -n todo-app \
  --create-namespace \
  --set frontend.image.tag=v1.0.0 \
  --set backend.image.tag=v1.0.0
```

---

### Method 3: Manual kubectl Deployment

For learning or debugging, deploy manually with kubectl.

#### Step 1: Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

#### Step 2: Create Secrets

```bash
kubectl apply -f k8s/secret.yaml
```

#### Step 3: Create ConfigMap

```bash
kubectl apply -f k8s/configmap.yaml
```

#### Step 4: Create PersistentVolumeClaim

```bash
kubectl apply -f k8s/postgres-pvc.yaml
```

#### Step 5: Deploy Database

```bash
kubectl apply -f k8s/database-deployment.yaml
kubectl apply -f k8s/database-service.yaml
```

Wait for database to be ready:
```bash
kubectl wait --for=condition=ready pod -l component=database -n todo-app --timeout=120s
```

#### Step 6: Deploy Backend

```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
```

Wait for backend to be ready:
```bash
kubectl wait --for=condition=ready pod -l component=backend -n todo-app --timeout=120s
```

#### Step 7: Deploy Frontend

```bash
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
```

Wait for frontend to be ready:
```bash
kubectl wait --for=condition=ready pod -l component=frontend -n todo-app --timeout=120s
```

#### Step 8: Configure Ingress

```bash
kubectl apply -f k8s/ingress.yaml
```

---

## Post-Deployment Verification

### 1. Check Deployment Status

**Quick Status:**
```bash
./scripts/status.sh  # Linux/macOS
scripts\status.bat   # Windows
```

**Manual Check:**
```bash
# Check all resources
kubectl get all -n todo-app

# Check pods
kubectl get pods -n todo-app

# Check services
kubectl get services -n todo-app

# Check ingress
kubectl get ingress -n todo-app
```

### 2. Verify Pod Health

```bash
# Check pod status
kubectl get pods -n todo-app -o wide

# Expected output:
# NAME                        READY   STATUS    RESTARTS   AGE
# backend-xxx                 1/1     Running   0          2m
# backend-yyy                 1/1     Running   0          2m
# database-zzz                1/1     Running   0          3m
# frontend-aaa                1/1     Running   0          2m
# frontend-bbb                1/1     Running   0          2m
```

All pods should show:
- READY: 1/1
- STATUS: Running
- RESTARTS: 0 (or low number)

### 3. Test Health Endpoints

**Backend Health:**
```bash
# Get backend pod
BACKEND_POD=$(kubectl get pods -n todo-app -l component=backend -o jsonpath='{.items[0].metadata.name}')

# Test health endpoint
kubectl exec -n todo-app $BACKEND_POD -- curl -s http://localhost:8000/health
```

Expected: `{"status":"healthy"}`

**Frontend Health:**
```bash
# Get frontend pod
FRONTEND_POD=$(kubectl get pods -n todo-app -l component=frontend -o jsonpath='{.items[0].metadata.name}')

# Test frontend
kubectl exec -n todo-app $FRONTEND_POD -- wget -q -O- http://localhost:3000
```

Expected: HTML content

### 4. Test Database Connectivity

```bash
# Test from backend pod
kubectl exec -n todo-app $BACKEND_POD -- pg_isready -h database -p 5432 -U postgres
```

Expected: `database:5432 - accepting connections`

### 5. Access Application

**Via Ingress:**
```bash
# Open in browser
open http://todo.local  # macOS
xdg-open http://todo.local  # Linux
start http://todo.local  # Windows
```

**Via Port Forwarding (if Ingress not working):**
```bash
# Frontend
kubectl port-forward service/frontend 3000:3000 -n todo-app
# Access: http://localhost:3000

# Backend
kubectl port-forward service/backend 8000:8000 -n todo-app
# Access: http://localhost:8000
```

### 6. Run Verification Script

**Comprehensive Verification:**
```bash
./scripts/verify.sh  # Linux/macOS
scripts\verify.bat   # Windows
```

**Deployment Verification:**
```bash
./scripts/verify-deployment.sh  # Linux/macOS
scripts\verify-deployment.bat   # Windows
```

### 7. Test CRUD Operations

1. **Create Todo:**
   - Visit http://todo.local
   - Click "Add Todo"
   - Enter title and description
   - Click "Save"

2. **Read Todos:**
   - Verify todo appears in list
   - Check details display correctly

3. **Update Todo:**
   - Click on todo
   - Edit title or description
   - Mark as complete
   - Verify changes persist

4. **Delete Todo:**
   - Click delete button
   - Confirm deletion
   - Verify todo is removed

5. **Test AI Chatbot (if OpenAI key configured):**
   - Open chatbot
   - Ask: "What are my todos?"
   - Ask: "Add a new todo: Buy groceries"
   - Verify responses and actions

---

## Configuration Management

### Updating ConfigMap

**Edit ConfigMap:**
```bash
kubectl edit configmap todo-app-config -n todo-app
```

**Or apply changes:**
```bash
# Edit k8s/configmap.yaml
kubectl apply -f k8s/configmap.yaml
```

**Restart deployments to apply:**
```bash
kubectl rollout restart deployment/backend -n todo-app
kubectl rollout restart deployment/frontend -n todo-app
```

### Updating Secrets

**Edit Secret:**
```bash
kubectl edit secret todo-app-secrets -n todo-app
```

**Or recreate:**
```bash
kubectl delete secret todo-app-secrets -n todo-app
kubectl create secret generic todo-app-secrets -n todo-app \
  --from-literal=POSTGRES_USER=postgres \
  --from-literal=POSTGRES_PASSWORD=newpassword \
  --from-literal=DATABASE_URL=postgresql://postgres:newpassword@database:5432/todo_db \
  --from-literal=SECRET_KEY=$(openssl rand -base64 32) \
  --from-literal=OPENAI_API_KEY=sk-...
```

**Restart deployments:**
```bash
kubectl rollout restart deployment/backend -n todo-app
```

### Environment-Specific Deployments

**Switch to Development:**
```bash
helm upgrade todo-app ./helm/todo-app -n todo-app -f helm/todo-app/values-dev.yaml
```

**Switch to Testing:**
```bash
helm upgrade todo-app ./helm/todo-app -n todo-app -f helm/todo-app/values-test.yaml
```

---

## Scaling and Updates

### Manual Scaling

**Scale Frontend:**
```bash
kubectl scale deployment/frontend --replicas=3 -n todo-app
```

**Scale Backend:**
```bash
kubectl scale deployment/backend --replicas=3 -n todo-app
```

**Verify Scaling:**
```bash
kubectl get deployments -n todo-app
```

### Helm-Based Scaling

```bash
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=3
```

### Rolling Updates

**Update Image Version:**
```bash
# Build new version
./scripts/build-images.sh v1.1.0

# Update deployment
kubectl set image deployment/backend backend=todo-backend:v1.1.0 -n todo-app
kubectl set image deployment/frontend frontend=todo-frontend:v1.1.0 -n todo-app
```

**Or with Helm:**
```bash
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set frontend.image.tag=v1.1.0 \
  --set backend.image.tag=v1.1.0
```

**Monitor Rollout:**
```bash
kubectl rollout status deployment/backend -n todo-app
kubectl rollout status deployment/frontend -n todo-app
```

---

## Rollback Procedures

### kubectl Rollback

**View Rollout History:**
```bash
kubectl rollout history deployment/backend -n todo-app
```

**Rollback to Previous Version:**
```bash
kubectl rollout undo deployment/backend -n todo-app
```

**Rollback to Specific Revision:**
```bash
kubectl rollout undo deployment/backend --to-revision=2 -n todo-app
```

### Helm Rollback

**View Release History:**
```bash
helm history todo-app -n todo-app
```

**Rollback to Previous Release:**
```bash
helm rollback todo-app -n todo-app
```

**Rollback to Specific Revision:**
```bash
helm rollback todo-app 2 -n todo-app
```

### Emergency Rollback

If deployment is completely broken:

```bash
# Delete everything
./scripts/cleanup.sh

# Redeploy previous working version
./scripts/build-images.sh v1.0.0
helm install todo-app ./helm/todo-app -n todo-app \
  --set frontend.image.tag=v1.0.0 \
  --set backend.image.tag=v1.0.0
```

---

## Troubleshooting

### Pods Not Starting

**Check pod status:**
```bash
kubectl get pods -n todo-app
kubectl describe pod <pod-name> -n todo-app
```

**Check logs:**
```bash
kubectl logs <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app --previous  # Previous container
```

**Common issues:**
- Image not found: Rebuild images
- Init container failing: Check database connectivity
- CrashLoopBackOff: Check application logs

### Database Connection Issues

**Check database pod:**
```bash
kubectl get pods -l component=database -n todo-app
kubectl logs deployment/database -n todo-app
```

**Test connectivity:**
```bash
kubectl exec -it deployment/backend -n todo-app -- \
  pg_isready -h database -p 5432 -U postgres
```

**Check secrets:**
```bash
kubectl get secret todo-app-secrets -n todo-app -o yaml
```

### Ingress Not Working

**Check Ingress controller:**
```bash
kubectl get pods -n ingress-nginx
```

**Check Ingress configuration:**
```bash
kubectl describe ingress todo-app-ingress -n todo-app
```

**Verify hosts file:**
```bash
cat /etc/hosts | grep todo.local  # Linux/macOS
type C:\Windows\System32\drivers\etc\hosts | findstr todo.local  # Windows
```

**Use port forwarding as workaround:**
```bash
kubectl port-forward service/frontend 3000:3000 -n todo-app
```

### Deployment Stuck

**Check events:**
```bash
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

**Force restart:**
```bash
kubectl rollout restart deployment/backend -n todo-app
kubectl rollout restart deployment/frontend -n todo-app
```

**Delete and recreate:**
```bash
kubectl delete deployment backend -n todo-app
kubectl apply -f k8s/backend-deployment.yaml
```

---

## Cleanup

### Remove Deployment

**Using Script:**
```bash
./scripts/cleanup.sh  # Linux/macOS
scripts\cleanup.bat   # Windows
```

**Using Helm:**
```bash
helm uninstall todo-app -n todo-app
kubectl delete namespace todo-app
```

**Manual Cleanup:**
```bash
kubectl delete -f k8s/ingress.yaml
kubectl delete -f k8s/frontend-service.yaml
kubectl delete -f k8s/frontend-deployment.yaml
kubectl delete -f k8s/backend-service.yaml
kubectl delete -f k8s/backend-deployment.yaml
kubectl delete -f k8s/database-service.yaml
kubectl delete -f k8s/database-deployment.yaml
kubectl delete -f k8s/postgres-pvc.yaml
kubectl delete -f k8s/configmap.yaml
kubectl delete -f k8s/secret.yaml
kubectl delete namespace todo-app
```

### Stop Minikube

```bash
minikube stop
```

### Delete Minikube Cluster

```bash
minikube delete
```

---

## Best Practices

### 1. Version Control

- Always tag images with versions
- Use semantic versioning (v1.0.0, v1.1.0, etc.)
- Keep track of deployed versions

### 2. Configuration Management

- Use Helm values files for different environments
- Never commit secrets to version control
- Use external secret management in production

### 3. Monitoring

- Regularly check pod health
- Monitor resource usage
- Set up alerts for failures

### 4. Backup

- Backup database regularly
- Export Kubernetes configurations
- Document custom changes

### 5. Testing

- Test in development environment first
- Verify all features after deployment
- Run automated tests

---

## Additional Resources

- **Setup Guide**: [SETUP.md](./SETUP.md)
- **Quick Reference**: [QUICK_REFERENCE.md](../QUICK_REFERENCE.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- **Architecture**: [ARCHITECTURE.md](../ARCHITECTURE.md)
- **Helm Chart**: [helm/todo-app/README.md](../helm/todo-app/README.md)

---

**Last Updated**: February 7, 2026
