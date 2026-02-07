# Quick Start Guide: Local Kubernetes Deployment

**Feature**: Phase IV - Local Kubernetes Deployment
**Date**: 2026-02-07
**Audience**: Developers deploying the Todo application to local Kubernetes

## Overview

This guide walks you through deploying the Phase III AI-Powered Todo Chatbot application to a local Kubernetes cluster (Minikube) using Docker, Helm, and AI-assisted tools. The entire deployment process takes approximately 10 minutes on a clean environment.

---

## Prerequisites

### Required Software

| Tool | Minimum Version | Purpose | Installation |
|------|----------------|---------|--------------|
| Docker | 24.0+ | Container runtime | [docker.com](https://www.docker.com/get-started) |
| Minikube | 1.30+ | Local Kubernetes cluster | [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | 1.28+ | Kubernetes CLI | [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/) |
| Helm | 3.12+ | Kubernetes package manager | [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |

### Optional AI Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| Docker AI (Gordon) | Generate Dockerfiles | [docs.docker.com/ai](https://docs.docker.com/ai/) |
| kubectl-ai | Natural language K8s commands | [github.com/sozercan/kubectl-ai](https://github.com/sozercan/kubectl-ai) |
| kagent | AI cluster management | [kagent.ai](https://kagent.ai) |

### System Requirements

- **RAM**: 8GB minimum (12GB recommended)
- **Disk Space**: 20GB free
- **OS**: Windows 10+, macOS 11+, or Ubuntu 20.04+
- **Network**: Internet access for pulling images

---

## Step 1: Verify Prerequisites

Run the validation script to check all prerequisites:

### Linux/macOS
```bash
cd phase-4-kubernetes
./scripts/validate-prerequisites.sh
```

### Windows
```cmd
cd phase-4-kubernetes
scripts\validate-prerequisites.bat
```

**Expected Output**:
```
✓ Docker installed (version 24.0.5)
✓ Minikube installed (version 1.31.2)
✓ kubectl installed (version 1.28.3)
✓ Helm installed (version 3.12.3)
✓ Docker daemon running
✓ System resources: 16GB RAM, 50GB disk available
✓ All prerequisites met!
```

---

## Step 2: Start Minikube Cluster

Initialize a local Kubernetes cluster with appropriate resources:

### Linux/macOS
```bash
./scripts/setup-minikube.sh
```

### Windows
```cmd
scripts\setup-minikube.bat
```

### Manual Setup (if script unavailable)
```bash
# Start Minikube with 8GB RAM and 4 CPUs
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable NGINX Ingress Controller
minikube addons enable ingress

# Enable metrics server for resource monitoring
minikube addons enable metrics-server

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

**Expected Output**:
```
😄  minikube v1.31.2 on Darwin 13.5
✨  Using the docker driver based on existing profile
👍  Starting control plane node minikube in cluster minikube
🚜  Pulling base image ...
🔄  Restarting existing docker container for "minikube" ...
🐳  Preparing Kubernetes v1.28.3 on Docker 24.0.5 ...
🔗  Configuring bridge CNI (Container Networking Interface) ...
🔎  Verifying Kubernetes components...
🌟  Enabled addons: ingress, metrics-server
🏄  Done! kubectl is now configured to use "minikube" cluster
```

---

## Step 3: Configure Local DNS

Add the application hostname to your hosts file:

### Linux/macOS
```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)
echo "$MINIKUBE_IP todo.local" | sudo tee -a /etc/hosts
```

### Windows (Run as Administrator)
```cmd
REM Get Minikube IP
minikube ip

REM Add to C:\Windows\System32\drivers\etc\hosts
REM <minikube-ip> todo.local
```

**Example**:
```
192.168.49.2 todo.local
```

---

## Step 4: Build Docker Images

Build container images for all services:

### Linux/macOS
```bash
./scripts/build-images.sh
```

### Windows
```cmd
scripts\build-images.bat
```

### Manual Build (if script unavailable)
```bash
# Configure Docker to use Minikube's Docker daemon
eval $(minikube docker-env)

# Build frontend image
docker build -t todo-frontend:latest -f docker/frontend/Dockerfile app/frontend/

# Build backend image
docker build -t todo-backend:latest -f docker/backend/Dockerfile app/backend/

# Verify images
docker images | grep todo
```

**Expected Output**:
```
Building frontend image...
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 1.2kB
 => [internal] load .dockerignore
 => => transferring context: 100B
 => [stage-0 1/4] FROM docker.io/library/node:18-alpine
 => CACHED [stage-0 2/4] WORKDIR /app
 => [stage-0 3/4] COPY package*.json ./
 => [stage-0 4/4] RUN npm ci
 => [stage-1 1/3] COPY --from=deps /app/node_modules ./node_modules
 => [stage-1 2/3] COPY . .
 => [stage-1 3/3] RUN npm run build
 => exporting to image
 => => exporting layers
 => => writing image sha256:abc123...
 => => naming to docker.io/library/todo-frontend:latest

Building backend image...
[+] Building 32.1s (10/10) FINISHED
...

✓ Frontend image built: todo-frontend:latest (150MB)
✓ Backend image built: todo-backend:latest (200MB)
```

---

## Step 5: Create Kubernetes Secrets

Create secrets for sensitive configuration:

```bash
# Create namespace
kubectl create namespace todo-app

# Create backend secrets
kubectl create secret generic backend-secrets \
  --from-literal=database-url="postgresql://todouser:todopass@database:5432/todos" \
  --from-literal=openai-api-key="sk-your-openai-api-key-here" \
  --from-literal=jwt-secret="your-jwt-secret-key-here" \
  --from-literal=secret-key="your-secret-key-here" \
  -n todo-app

# Create database secrets
kubectl create secret generic database-secrets \
  --from-literal=postgres-password="todopass" \
  --from-literal=postgres-user="todouser" \
  --from-literal=postgres-db="todos" \
  -n todo-app

# Verify secrets
kubectl get secrets -n todo-app
```

**Important**: Replace placeholder values with actual secrets. Never commit secrets to version control.

---

## Step 6: Deploy with Helm

Deploy the entire application stack with a single command:

### Development Deployment
```bash
helm install todo-app ./helm/todo-app -f ./helm/todo-app/values-dev.yaml -n todo-app
```

### Default Deployment
```bash
helm install todo-app ./helm/todo-app -n todo-app
```

### Custom Configuration
```bash
helm install todo-app ./helm/todo-app \
  --set frontend.replicaCount=2 \
  --set backend.replicaCount=2 \
  --set backend.image.tag=1.0.0 \
  -n todo-app
```

**Expected Output**:
```
NAME: todo-app
LAST DEPLOYED: Fri Feb  7 10:00:00 2026
NAMESPACE: todo-app
STATUS: deployed
REVISION: 1
NOTES:
🎉 Todo App has been deployed!

1. Wait for all pods to be ready:
   kubectl get pods -n todo-app -w

2. Access the application:
   http://todo.local

3. Check service status:
   kubectl get svc -n todo-app

4. View logs:
   kubectl logs -f deployment/backend -n todo-app
   kubectl logs -f deployment/frontend -n todo-app

5. Scale services:
   kubectl scale deployment backend --replicas=3 -n todo-app

For troubleshooting, see: docs/TROUBLESHOOTING.md
```

---

## Step 7: Verify Deployment

Check that all services are running:

```bash
# Watch pods until all are Running
kubectl get pods -n todo-app -w

# Check service endpoints
kubectl get svc -n todo-app

# Check ingress
kubectl get ingress -n todo-app

# Check resource usage
kubectl top pods -n todo-app
```

**Expected Output**:
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-7d8f9c5b6-xk2lm    1/1     Running   0          2m
backend-7d8f9c5b6-zn4pq    1/1     Running   0          2m
frontend-6c9d8f5b4-abc12   1/1     Running   0          2m
frontend-6c9d8f5b4-def34   1/1     Running   0          2m
database-0                  1/1     Running   0          2m

NAME       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
backend    ClusterIP   10.96.100.10    <none>        8000/TCP   2m
frontend   ClusterIP   10.96.100.20    <none>        3000/TCP   2m
database   ClusterIP   None            <none>        5432/TCP   2m

NAME           CLASS   HOSTS        ADDRESS          PORTS   AGE
todo-ingress   nginx   todo.local   192.168.49.2     80      2m
```

---

## Step 8: Access the Application

Open your browser and navigate to:

```
http://todo.local
```

You should see the Todo application login page. Create an account and start using the AI-powered chatbot!

### Testing the API
```bash
# Health check
curl http://todo.local/api/health

# Register user
curl -X POST http://todo.local/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"testpass123"}'

# Login
curl -X POST http://todo.local/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

---

## AI-Assisted Operations (Optional)

If you have kubectl-ai or kagent installed, you can use natural language commands:

### kubectl-ai Examples
```bash
# Check pod status
kubectl-ai "show me all pods in todo-app namespace"

# Scale backend
kubectl-ai "scale the backend deployment to 3 replicas"

# View logs
kubectl-ai "show me the last 50 lines of backend logs"

# Troubleshoot
kubectl-ai "why is the frontend pod crashing?"
```

### kagent Examples
```bash
# Analyze cluster health
kagent "analyze the cluster health"

# Optimize resources
kagent "suggest resource optimizations for todo-app"

# Check for issues
kagent "are there any issues with the deployment?"
```

---

## Common Operations

### Scaling Services
```bash
# Scale backend to 3 replicas
kubectl scale deployment backend --replicas=3 -n todo-app

# Scale frontend to 2 replicas
kubectl scale deployment frontend --replicas=2 -n todo-app
```

### Viewing Logs
```bash
# Follow backend logs
kubectl logs -f deployment/backend -n todo-app

# Follow frontend logs
kubectl logs -f deployment/frontend -n todo-app

# View database logs
kubectl logs -f statefulset/database -n todo-app

# View logs from specific pod
kubectl logs backend-7d8f9c5b6-xk2lm -n todo-app
```

### Restarting Services
```bash
# Restart backend
kubectl rollout restart deployment/backend -n todo-app

# Restart frontend
kubectl rollout restart deployment/frontend -n todo-app

# Check rollout status
kubectl rollout status deployment/backend -n todo-app
```

### Updating Configuration
```bash
# Update Helm values
helm upgrade todo-app ./helm/todo-app \
  --set backend.replicaCount=3 \
  -n todo-app

# Verify upgrade
helm list -n todo-app
helm history todo-app -n todo-app
```

---

## Cleanup

### Uninstall Application
```bash
# Uninstall Helm release
helm uninstall todo-app -n todo-app

# Delete namespace (removes all resources)
kubectl delete namespace todo-app

# Or use cleanup script
./scripts/cleanup.sh  # Linux/macOS
scripts\cleanup.bat   # Windows
```

### Stop Minikube
```bash
# Stop cluster (preserves state)
minikube stop

# Delete cluster (removes all data)
minikube delete
```

---

## Troubleshooting

### Pods Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check resource usage
kubectl top nodes
kubectl top pods -n todo-app
```

### Image Pull Errors
```bash
# Verify images exist in Minikube
eval $(minikube docker-env)
docker images | grep todo

# Rebuild images if missing
./scripts/build-images.sh
```

### Ingress Not Working
```bash
# Check Ingress addon
minikube addons list | grep ingress

# Enable if disabled
minikube addons enable ingress

# Check Ingress controller
kubectl get pods -n ingress-nginx

# Verify hosts file
cat /etc/hosts | grep todo.local  # Linux/macOS
type C:\Windows\System32\drivers\etc\hosts | findstr todo.local  # Windows
```

### Database Connection Issues
```bash
# Check database pod
kubectl get pod database-0 -n todo-app

# Check database logs
kubectl logs database-0 -n todo-app

# Test database connection
kubectl exec -it database-0 -n todo-app -- psql -U todouser -d todos
```

For more troubleshooting, see [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)

---

## Next Steps

1. **Explore the Application**: Create todos, use the AI chatbot, test all features
2. **Monitor Resources**: Use `kubectl top` to observe resource usage
3. **Test Scaling**: Scale services up and down to test load handling
4. **Review Logs**: Familiarize yourself with log output and error messages
5. **Experiment with Configuration**: Try different Helm values and observe changes

---

## Additional Resources

- **Architecture Overview**: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- **Deployment Guide**: [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md)
- **Scaling Guide**: [docs/SCALING.md](../docs/SCALING.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
- **Kubernetes Documentation**: [kubernetes.io/docs](https://kubernetes.io/docs/)
- **Helm Documentation**: [helm.sh/docs](https://helm.sh/docs/)
- **Minikube Documentation**: [minikube.sigs.k8s.io/docs](https://minikube.sigs.k8s.io/docs/)

---

## Support

If you encounter issues:
1. Check the troubleshooting guide
2. Review pod logs and events
3. Verify all prerequisites are met
4. Ensure sufficient system resources
5. Check the GitHub issues page for known problems

**Happy Deploying! 🚀**
