# Phase IV - Quick Start Guide

This guide will help you deploy the Todo App to a local Kubernetes cluster using Minikube in under 10 minutes.

## Prerequisites

Before starting, ensure you have:
- Docker 24.0+ installed and running
- Minikube 1.30+ installed
- kubectl 1.28+ installed
- Helm 3.12+ installed
- 8GB RAM available
- 20GB free disk space

## Quick Start (5 Steps)

### Step 1: Validate Prerequisites

**Linux/macOS:**
```bash
./scripts/validate-prerequisites.sh
```

**Windows:**
```cmd
scripts\validate-prerequisites.bat
```

This will check if all required tools are installed and properly configured.

### Step 2: Start Minikube

**Linux/macOS:**
```bash
./scripts/setup-minikube.sh
```

**Windows:**
```cmd
scripts\setup-minikube.bat
```

This will:
- Start Minikube with 4 CPUs, 8GB RAM, 20GB disk
- Enable Ingress controller
- Enable Metrics server

### Step 3: Add Hosts Entry

Get your Minikube IP:
```bash
minikube ip
```

Add this line to your hosts file (replace `<MINIKUBE_IP>` with actual IP):
```
<MINIKUBE_IP> todo.local
```

**Linux/macOS:**
```bash
sudo nano /etc/hosts
```

**Windows (Run as Administrator):**
```cmd
notepad C:\Windows\System32\drivers\etc\hosts
```

### Step 4: Build Docker Images

**Linux/macOS:**
```bash
./scripts/build-images.sh
```

**Windows:**
```cmd
scripts\build-images.bat
```

This will build both frontend and backend images using Minikube's Docker daemon.

### Step 5: Deploy Application

**Linux/macOS:**
```bash
./scripts/deploy.sh
```

**Windows:**
```cmd
scripts\deploy.bat
```

This will:
- Create namespace
- Deploy database (PostgreSQL)
- Deploy backend (FastAPI)
- Deploy frontend (Next.js)
- Configure Ingress

## Verify Deployment

Check the status:

**Linux/macOS:**
```bash
./scripts/status.sh
```

**Windows:**
```cmd
scripts\status.bat
```

Or manually:
```bash
kubectl get pods -n todo-app
kubectl get services -n todo-app
kubectl get ingress -n todo-app
```

## Access the Application

Once all pods are running, open your browser:
```
http://todo.local
```

The API is available at:
```
http://todo.local/api
```

## Common Operations

### View Logs

**Backend:**
```bash
kubectl logs -f deployment/backend -n todo-app
```

**Frontend:**
```bash
kubectl logs -f deployment/frontend -n todo-app
```

**Database:**
```bash
kubectl logs -f deployment/database -n todo-app
```

### Scale Services

**Using Helper Script:**
```bash
# Scale frontend to 3 replicas
./scripts/scale-service.sh frontend 3  # Linux/macOS
scripts\scale-service.bat frontend 3   # Windows

# Scale backend to 5 replicas
./scripts/scale-service.sh backend 5

# Scale both to 3 replicas
./scripts/scale-service.sh all 3
```

**Using kubectl:**
```bash
# Scale backend to 3 replicas
kubectl scale deployment/backend --replicas=3 -n todo-app

# Scale frontend to 3 replicas
kubectl scale deployment/frontend --replicas=3 -n todo-app
```

**Using Helm:**
```bash
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=3
```

### Monitor Resource Usage

**Real-Time Pod Metrics:**
```bash
# View CPU and memory usage
kubectl top pods -n todo-app

# Sort by CPU
kubectl top pods -n todo-app --sort-by=cpu

# Sort by memory
kubectl top pods -n todo-app --sort-by=memory

# Watch in real-time
watch kubectl top pods -n todo-app
```

**Node Metrics:**
```bash
# View node resource usage
kubectl top nodes

# Watch in real-time
watch kubectl top nodes
```

**Deployment Status:**
```bash
# Check deployment status
kubectl get deployments -n todo-app

# Check pod distribution
kubectl get pods -n todo-app -o wide

# Check resource requests and limits
kubectl describe deployment backend -n todo-app | grep -A 5 "Limits\|Requests"
```

**Horizontal Pod Autoscaler (HPA):**
```bash
# Check HPA status (if enabled)
kubectl get hpa -n todo-app

# Detailed HPA information
kubectl describe hpa -n todo-app

# Watch HPA in real-time
watch kubectl get hpa -n todo-app
```

### Enable Autoscaling

**Enable HPA via Helm:**
```bash
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set autoscaling.enabled=true \
  --set autoscaling.frontend.minReplicas=2 \
  --set autoscaling.frontend.maxReplicas=10 \
  --set autoscaling.backend.minReplicas=2 \
  --set autoscaling.backend.maxReplicas=10
```

**Monitor Autoscaling:**
```bash
# Watch HPA decisions
kubectl get hpa -n todo-app --watch

# View scaling events
kubectl get events -n todo-app | grep -i scale
```

### Port Forwarding (Alternative Access)

If Ingress is not working, use port forwarding:

```bash
# Frontend
kubectl port-forward service/frontend 3000:3000 -n todo-app

# Backend
kubectl port-forward service/backend 8000:8000 -n todo-app
```

Then access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

### Restart Deployments

```bash
kubectl rollout restart deployment/backend -n todo-app
kubectl rollout restart deployment/frontend -n todo-app
```

### Update Configuration

Edit ConfigMap:
```bash
kubectl edit configmap todo-app-config -n todo-app
```

Edit Secrets:
```bash
kubectl edit secret todo-app-secrets -n todo-app
```

After editing, restart deployments to apply changes.

## Troubleshooting

### Pods Not Starting

Check pod status:
```bash
kubectl describe pod <pod-name> -n todo-app
```

Check events:
```bash
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

### Database Connection Issues

Check database logs:
```bash
kubectl logs deployment/database -n todo-app
```

Verify database is ready:
```bash
kubectl exec -it deployment/database -n todo-app -- pg_isready -U postgres
```

### Ingress Not Working

Check Ingress controller:
```bash
kubectl get pods -n ingress-nginx
```

Check Ingress configuration:
```bash
kubectl describe ingress todo-app-ingress -n todo-app
```

Verify hosts file entry:
```bash
# Linux/macOS
cat /etc/hosts | grep todo.local

# Windows
type C:\Windows\System32\drivers\etc\hosts | findstr todo.local
```

### Image Pull Errors

Ensure you're using Minikube's Docker daemon:

**Linux/macOS:**
```bash
eval $(minikube docker-env)
docker images | grep todo-
```

**Windows:**
```cmd
@FOR /f "tokens=*" %i IN ('minikube docker-env --shell cmd') DO @%i
docker images | findstr todo-
```

If images are missing, rebuild:
```bash
./scripts/build-images.sh  # or .bat on Windows
```

## Cleanup

To remove all resources:

**Linux/macOS:**
```bash
./scripts/cleanup.sh
```

**Windows:**
```cmd
scripts\cleanup.bat
```

To completely remove Minikube:
```bash
minikube delete
```

## Next Steps

- Configure secrets in `k8s/secret.yaml` for production use
- Add your OpenAI API key for AI chatbot functionality
- Explore Helm charts for easier deployment management
- Set up monitoring with Prometheus and Grafana
- Configure persistent backups for the database

## Support

For issues or questions:
1. Check the main README.md
2. Review Kubernetes events: `kubectl get events -n todo-app`
3. Check pod logs: `kubectl logs <pod-name> -n todo-app`
4. Verify prerequisites: `./scripts/validate-prerequisites.sh`

## Success Criteria

Your deployment is successful when:
- ✓ All pods are in "Running" state
- ✓ All pods show "Ready" status (e.g., 1/1, 2/2)
- ✓ Ingress has an address assigned
- ✓ Application is accessible at http://todo.local
- ✓ API responds at http://todo.local/api/health
- ✓ You can create, read, update, and delete todos
- ✓ AI chatbot responds to queries (if OpenAI key configured)
