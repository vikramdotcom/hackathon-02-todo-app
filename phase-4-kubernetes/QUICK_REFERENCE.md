# Phase IV - Quick Reference

## One-Command Deployment

### Option 1: Direct Kubernetes (Recommended for first-time)

```bash
# Complete setup in 5 commands
./scripts/validate-prerequisites.sh
./scripts/setup-minikube.sh
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
./scripts/build-images.sh
./scripts/deploy.sh
```

**Access**: http://todo.local

### Option 2: Helm Deployment (Recommended for production)

```bash
# Same setup, different deployment
./scripts/validate-prerequisites.sh
./scripts/setup-minikube.sh
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
./scripts/build-images.sh
./scripts/helm-deploy.sh
```

**Access**: http://todo.local

---

## Common Commands

### Status & Monitoring

```bash
# Check deployment status
./scripts/status.sh

# Verify deployment health
./scripts/verify.sh

# View logs
kubectl logs -f deployment/backend -n todo-app
kubectl logs -f deployment/frontend -n todo-app
kubectl logs -f deployment/database -n todo-app

# Check resource usage
kubectl top pods -n todo-app
kubectl top nodes
```

### Scaling

```bash
# Scale backend
kubectl scale deployment/backend --replicas=3 -n todo-app

# Scale frontend
kubectl scale deployment/frontend --replicas=3 -n todo-app

# Check scaling status
kubectl get deployments -n todo-app
```

### Troubleshooting

```bash
# Get all resources
kubectl get all -n todo-app

# Describe a pod
kubectl describe pod <pod-name> -n todo-app

# Get events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check pod logs
kubectl logs <pod-name> -n todo-app

# Execute commands in pod
kubectl exec -it <pod-name> -n todo-app -- /bin/sh
```

### Cleanup

```bash
# Remove all resources
./scripts/cleanup.sh

# Or with Helm
helm uninstall todo-app -n todo-app

# Delete Minikube cluster
minikube delete
```

---

## Testing

### Validate Configuration

```bash
# Validate Kubernetes manifests
./tests/k8s-validate.sh

# Validate Helm chart
./tests/helm-lint.sh

# Run end-to-end test
./tests/deployment-test.sh
```

### Manual Testing

```bash
# 1. Deploy application
./scripts/deploy.sh

# 2. Wait for pods to be ready
kubectl wait --for=condition=ready pod --all -n todo-app --timeout=300s

# 3. Check health
curl http://todo.local/api/health

# 4. Test frontend
open http://todo.local  # macOS
xdg-open http://todo.local  # Linux
start http://todo.local  # Windows

# 5. Test CRUD operations
# - Create a todo
# - Mark as complete
# - Edit todo
# - Delete todo

# 6. Test AI chatbot (if OpenAI key configured)
# - Ask: "What are my todos?"
# - Ask: "Add a new todo: Buy groceries"
```

---

## Configuration

### Update Secrets

```bash
# Edit secrets
kubectl edit secret todo-app-secrets -n todo-app

# Or recreate from file
kubectl delete secret todo-app-secrets -n todo-app
kubectl create secret generic todo-app-secrets -n todo-app \
  --from-literal=POSTGRES_USER=postgres \
  --from-literal=POSTGRES_PASSWORD=newpassword \
  --from-literal=DATABASE_URL=postgresql://postgres:newpassword@database:5432/todo_db \
  --from-literal=SECRET_KEY=$(openssl rand -base64 32) \
  --from-literal=OPENAI_API_KEY=sk-...

# Restart deployments to apply
kubectl rollout restart deployment/backend -n todo-app
```

### Update Configuration

```bash
# Edit ConfigMap
kubectl edit configmap todo-app-config -n todo-app

# Restart deployments to apply
kubectl rollout restart deployment/backend -n todo-app
kubectl rollout restart deployment/frontend -n todo-app
```

### Helm Values

```bash
# View current values
helm get values todo-app -n todo-app

# Upgrade with new values
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=3

# Or with values file
helm upgrade todo-app ./helm/todo-app -n todo-app -f custom-values.yaml
```

---

## Helm Operations

### Install

```bash
# Basic install
helm install todo-app ./helm/todo-app -n todo-app --create-namespace

# With custom values
helm install todo-app ./helm/todo-app -n todo-app -f values-prod.yaml

# Dry run (test)
helm install todo-app ./helm/todo-app -n todo-app --dry-run --debug
```

### Upgrade

```bash
# Upgrade release
helm upgrade todo-app ./helm/todo-app -n todo-app

# Upgrade with new values
helm upgrade todo-app ./helm/todo-app -n todo-app --set backend.replicaCount=3

# Force upgrade
helm upgrade todo-app ./helm/todo-app -n todo-app --force
```

### Rollback

```bash
# View history
helm history todo-app -n todo-app

# Rollback to previous
helm rollback todo-app -n todo-app

# Rollback to specific revision
helm rollback todo-app 2 -n todo-app
```

### Uninstall

```bash
# Uninstall release
helm uninstall todo-app -n todo-app

# Keep history
helm uninstall todo-app -n todo-app --keep-history
```

---

## Port Forwarding (Alternative Access)

If Ingress is not working:

```bash
# Frontend
kubectl port-forward service/frontend 3000:3000 -n todo-app
# Access: http://localhost:3000

# Backend
kubectl port-forward service/backend 8001:8000 -n todo-app
# Access: http://localhost:8001

# Database (for debugging)
kubectl port-forward service/database 5432:5432 -n todo-app
# Connect: psql -h localhost -U postgres -d todo_db
```

---

## Minikube Operations

### Start/Stop

```bash
# Start Minikube
minikube start

# Stop Minikube
minikube stop

# Delete cluster
minikube delete

# Get cluster info
minikube status
minikube ip
```

### Docker Environment

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Verify
docker images | grep todo-

# Reset to host Docker
eval $(minikube docker-env -u)
```

### Addons

```bash
# List addons
minikube addons list

# Enable addon
minikube addons enable metrics-server

# Disable addon
minikube addons disable metrics-server
```

### Dashboard

```bash
# Open Kubernetes dashboard
minikube dashboard

# Get dashboard URL
minikube dashboard --url
```

---

## Troubleshooting Quick Fixes

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo-app

# Describe pod
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app

# Delete and recreate
kubectl delete pod <pod-name> -n todo-app
```

### Images Not Found

```bash
# Ensure using Minikube's Docker
eval $(minikube docker-env)

# Rebuild images
./scripts/build-images.sh

# Verify images
docker images | grep todo-
```

### Ingress Not Working

```bash
# Check Ingress controller
kubectl get pods -n ingress-nginx

# Restart Ingress addon
minikube addons disable ingress
minikube addons enable ingress

# Verify hosts file
cat /etc/hosts | grep todo.local
```

### Database Connection Issues

```bash
# Check database pod
kubectl get pods -l component=database -n todo-app

# Check database logs
kubectl logs deployment/database -n todo-app

# Test connection from backend
kubectl exec -it deployment/backend -n todo-app -- \
  pg_isready -h database -p 5432 -U postgres
```

### Complete Reset

```bash
# Nuclear option - start fresh
./scripts/cleanup.sh
minikube delete
./scripts/setup-minikube.sh
./scripts/build-images.sh
./scripts/deploy.sh
```

---

## Performance Tuning

### Increase Resources

```bash
# Stop Minikube
minikube stop

# Start with more resources
minikube start --cpus=6 --memory=12288 --disk-size=30g

# Or delete and recreate
minikube delete
minikube start --cpus=6 --memory=12288 --disk-size=30g
```

### Optimize Images

```bash
# Use multi-stage builds (already implemented)
# Images are optimized for size and performance

# Check image sizes
docker images | grep todo-
```

### Scale Services

```bash
# Scale up for better performance
kubectl scale deployment/backend --replicas=4 -n todo-app
kubectl scale deployment/frontend --replicas=4 -n todo-app

# Monitor resource usage
kubectl top pods -n todo-app
```

---

## Documentation

- **README.md** - Phase IV overview
- **QUICKSTART.md** - 5-step deployment guide
- **TROUBLESHOOTING.md** - Comprehensive issue resolution
- **ARCHITECTURE.md** - System architecture and design
- **IMPLEMENTATION_STATUS.md** - Implementation progress
- **helm/todo-app/README.md** - Helm chart documentation

---

## Support

For detailed information, see:
- Full documentation in `phase-4-kubernetes/` directory
- Troubleshooting guide: `TROUBLESHOOTING.md`
- Architecture details: `ARCHITECTURE.md`
- Helm chart docs: `helm/todo-app/README.md`

---

**Last Updated**: February 7, 2026
