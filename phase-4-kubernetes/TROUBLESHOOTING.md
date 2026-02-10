# Phase IV - Troubleshooting Guide

This guide covers common issues and their solutions when deploying the Todo App to Kubernetes.

## Table of Contents

1. [Prerequisites Issues](#prerequisites-issues)
2. [Minikube Issues](#minikube-issues)
3. [Docker Issues](#docker-issues)
4. [Deployment Issues](#deployment-issues)
5. [Networking Issues](#networking-issues)
6. [Database Issues](#database-issues)
7. [Performance Issues](#performance-issues)
8. [Configuration Issues](#configuration-issues)

---

## Prerequisites Issues

### Docker Not Found

**Symptom:** `docker: command not found`

**Solution:**
1. Install Docker Desktop from https://www.docker.com/get-started
2. Start Docker Desktop
3. Verify: `docker --version`

### Docker Daemon Not Running

**Symptom:** `Cannot connect to the Docker daemon`

**Solution:**
1. Start Docker Desktop
2. Wait for Docker to fully start (check system tray icon)
3. Verify: `docker info`

### Insufficient System Resources

**Symptom:** Minikube fails to start with memory/CPU errors

**Solution:**
1. Close unnecessary applications
2. Ensure at least 8GB RAM available
3. Adjust Minikube settings in `scripts/setup-minikube.sh`:
   ```bash
   CPUS=2  # Reduce from 4
   MEMORY=4096  # Reduce from 8192
   ```

---

## Minikube Issues

### Minikube Won't Start

**Symptom:** `minikube start` fails

**Solution 1 - Driver Issues:**
```bash
# Try different driver
minikube start --driver=virtualbox
# or
minikube start --driver=hyperv  # Windows
```

**Solution 2 - Clean Start:**
```bash
minikube delete
minikube start
```

**Solution 3 - Check Logs:**
```bash
minikube logs
```

### Minikube IP Not Accessible

**Symptom:** Cannot reach Minikube IP

**Solution:**
```bash
# Get IP
minikube ip

# Test connectivity
ping $(minikube ip)

# Check Minikube status
minikube status

# Restart if needed
minikube stop
minikube start
```

### Ingress Addon Not Working

**Symptom:** Ingress controller pods not running

**Solution:**
```bash
# Check addon status
minikube addons list

# Disable and re-enable
minikube addons disable ingress
minikube addons enable ingress

# Wait for controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

---

## Docker Issues

### Images Not Found

**Symptom:** `ImagePullBackOff` or `ErrImagePull`

**Solution:**
```bash
# Ensure using Minikube's Docker daemon
eval $(minikube docker-env)  # Linux/macOS
# or
@FOR /f "tokens=*" %i IN ('minikube docker-env --shell cmd') DO @%i  # Windows

# Verify images exist
docker images | grep todo-

# Rebuild if missing
./scripts/build-images.sh
```

### Build Failures

**Symptom:** Docker build fails

**Solution 1 - Frontend Build:**
```bash
# Check Node.js version in Phase III
cd phase-3-ai-chatbot/frontend
node --version  # Should be 18+

# Check for build errors
npm install
npm run build
```

**Solution 2 - Backend Build:**
```bash
# Check Python version
cd phase-3-ai-chatbot/backend
python --version  # Should be 3.11+

# Check dependencies
pip install -r requirements.txt
```

**Solution 3 - Clean Build:**
```bash
# Remove Docker cache
docker system prune -a
# Rebuild
./scripts/build-images.sh
```

---

## Deployment Issues

### Pods Stuck in Pending

**Symptom:** Pods remain in "Pending" state

**Solution:**
```bash
# Check pod details
kubectl describe pod <pod-name> -n todo-app

# Common causes:
# 1. Insufficient resources
kubectl top nodes

# 2. PVC not bound
kubectl get pvc -n todo-app

# 3. Node selector issues
kubectl get nodes --show-labels
```

### Pods Crashing (CrashLoopBackOff)

**Symptom:** Pods repeatedly crash

**Solution:**
```bash
# Check logs
kubectl logs <pod-name> -n todo-app --previous

# Common causes:
# 1. Database not ready (backend)
# 2. Missing environment variables
# 3. Application errors

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

### Init Container Failures

**Symptom:** Backend pods stuck waiting for database

**Solution:**
```bash
# Check database status
kubectl get pods -l component=database -n todo-app

# Check database logs
kubectl logs deployment/database -n todo-app

# Verify database is ready
kubectl exec -it deployment/database -n todo-app -- pg_isready -U postgres

# Check init container logs
kubectl logs <backend-pod> -c wait-for-db -n todo-app
```

### Deployment Rollout Stuck

**Symptom:** Deployment not progressing

**Solution:**
```bash
# Check rollout status
kubectl rollout status deployment/backend -n todo-app

# Check deployment events
kubectl describe deployment backend -n todo-app

# Force restart
kubectl rollout restart deployment/backend -n todo-app

# Rollback if needed
kubectl rollout undo deployment/backend -n todo-app
```

---

## Networking Issues

### Cannot Access Application

**Symptom:** `http://todo.local` not accessible

**Solution 1 - Hosts File:**
```bash
# Verify hosts entry
# Linux/macOS
cat /etc/hosts | grep todo.local

# Windows
type C:\Windows\System32\drivers\etc\hosts | findstr todo.local

# Should show: <MINIKUBE_IP> todo.local
```

**Solution 2 - Ingress:**
```bash
# Check Ingress status
kubectl get ingress -n todo-app

# Should show ADDRESS column populated
# If empty, wait or check Ingress controller

# Describe Ingress
kubectl describe ingress todo-app-ingress -n todo-app
```

**Solution 3 - Port Forwarding (Workaround):**
```bash
# Frontend
kubectl port-forward service/frontend 3000:3000 -n todo-app
# Access: http://localhost:3000

# Backend
kubectl port-forward service/backend 8001:8000 -n todo-app
# Access: http://localhost:8001
```

### Service Not Reachable

**Symptom:** Services cannot communicate

**Solution:**
```bash
# Check services
kubectl get services -n todo-app

# Test service connectivity from a pod
kubectl run test-pod --rm -it --image=busybox -n todo-app -- sh
# Inside pod:
wget -O- http://backend:8000/health
wget -O- http://frontend:3000

# Check service endpoints
kubectl get endpoints -n todo-app
```

### DNS Resolution Issues

**Symptom:** Pods cannot resolve service names

**Solution:**
```bash
# Check CoreDNS
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Test DNS from pod
kubectl exec -it <pod-name> -n todo-app -- nslookup backend

# Restart CoreDNS if needed
kubectl rollout restart deployment/coredns -n kube-system
```

---

## Database Issues

### Database Not Starting

**Symptom:** Database pod fails to start

**Solution:**
```bash
# Check logs
kubectl logs deployment/database -n todo-app

# Check PVC
kubectl get pvc postgres-pvc -n todo-app

# If PVC stuck, check storage class
kubectl get storageclass

# Delete and recreate if needed
kubectl delete pvc postgres-pvc -n todo-app
kubectl apply -f k8s/postgres-pvc.yaml
```

### Connection Refused

**Symptom:** Backend cannot connect to database

**Solution:**
```bash
# Verify database is running
kubectl get pods -l component=database -n todo-app

# Check database service
kubectl get service database -n todo-app

# Test connection from backend pod
kubectl exec -it deployment/backend -n todo-app -- \
  pg_isready -h database -p 5432 -U postgres

# Check DATABASE_URL secret
kubectl get secret todo-app-secrets -n todo-app -o yaml
```

### Migration Failures

**Symptom:** Alembic migrations fail

**Solution:**
```bash
# Check backend logs for migration errors
kubectl logs deployment/backend -n todo-app | grep alembic

# Manually run migrations
kubectl exec -it deployment/backend -n todo-app -- alembic upgrade head

# Reset database if needed (CAUTION: data loss)
kubectl exec -it deployment/database -n todo-app -- \
  psql -U postgres -c "DROP DATABASE todo_db; CREATE DATABASE todo_db;"
```

### Data Persistence Issues

**Symptom:** Data lost after pod restart

**Solution:**
```bash
# Verify PVC is bound
kubectl get pvc postgres-pvc -n todo-app

# Check PV
kubectl get pv

# Verify volume mount
kubectl describe pod <database-pod> -n todo-app | grep -A 5 Mounts

# Check PGDATA path
kubectl exec -it deployment/database -n todo-app -- ls -la /var/lib/postgresql/data/pgdata
```

---

## Performance Issues

### Slow Response Times

**Symptom:** Application is slow

**Solution:**
```bash
# Check resource usage
kubectl top pods -n todo-app
kubectl top nodes

# Check pod limits
kubectl describe pod <pod-name> -n todo-app | grep -A 5 Limits

# Scale up if needed
kubectl scale deployment/backend --replicas=3 -n todo-app
kubectl scale deployment/frontend --replicas=3 -n todo-app

# Increase resource limits in deployment YAML
```

### Out of Memory (OOMKilled)

**Symptom:** Pods killed due to memory

**Solution:**
```bash
# Check events
kubectl get events -n todo-app | grep OOM

# Increase memory limits
# Edit deployment YAML:
resources:
  limits:
    memory: "1Gi"  # Increase from 512Mi

# Apply changes
kubectl apply -f k8s/backend-deployment.yaml
```

### High CPU Usage

**Symptom:** CPU throttling

**Solution:**
```bash
# Check CPU usage
kubectl top pods -n todo-app

# Increase CPU limits
resources:
  limits:
    cpu: "1000m"  # Increase from 500m

# Scale horizontally
kubectl scale deployment/backend --replicas=3 -n todo-app
```

---

## Configuration Issues

### Environment Variables Not Set

**Symptom:** Application errors due to missing config

**Solution:**
```bash
# Check ConfigMap
kubectl get configmap todo-app-config -n todo-app -o yaml

# Check Secrets
kubectl get secret todo-app-secrets -n todo-app -o yaml

# Verify pod environment
kubectl exec -it <pod-name> -n todo-app -- env | grep -i database

# Update and restart
kubectl edit configmap todo-app-config -n todo-app
kubectl rollout restart deployment/backend -n todo-app
```

### Secret Not Found

**Symptom:** `Error: secret "todo-app-secrets" not found`

**Solution:**
```bash
# Create secret from example
cp k8s/secret.yaml.example k8s/secret.yaml

# Edit with your values
nano k8s/secret.yaml

# Apply
kubectl apply -f k8s/secret.yaml

# Verify
kubectl get secret todo-app-secrets -n todo-app
```

### OpenAI API Key Issues

**Symptom:** AI chatbot not working

**Solution:**
```bash
# Update secret with API key
kubectl edit secret todo-app-secrets -n todo-app

# Add base64-encoded key:
# echo -n "your-api-key" | base64

# Restart backend
kubectl rollout restart deployment/backend -n todo-app

# Verify in logs
kubectl logs deployment/backend -n todo-app | grep -i openai
```

---

## General Debugging Commands

### Get All Resources
```bash
kubectl get all -n todo-app
```

### Check Events
```bash
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

### Describe Resource
```bash
kubectl describe <resource-type> <resource-name> -n todo-app
```

### View Logs
```bash
kubectl logs <pod-name> -n todo-app
kubectl logs <pod-name> -c <container-name> -n todo-app
kubectl logs -f deployment/<deployment-name> -n todo-app
```

### Execute Commands in Pod
```bash
kubectl exec -it <pod-name> -n todo-app -- /bin/sh
```

### Port Forward
```bash
kubectl port-forward <pod-name> <local-port>:<pod-port> -n todo-app
```

### Copy Files
```bash
kubectl cp <pod-name>:/path/to/file ./local-file -n todo-app
```

---

## Getting Help

If issues persist:

1. **Check Logs:** Always start with pod logs
2. **Check Events:** Look for recent events in the namespace
3. **Verify Prerequisites:** Run validation script again
4. **Clean Slate:** Try cleanup and redeploy
5. **Minikube Logs:** Check `minikube logs` for cluster issues
6. **Community:** Search Kubernetes/Minikube documentation

## Emergency Reset

If all else fails:

```bash
# Complete cleanup
./scripts/cleanup.sh
minikube delete

# Fresh start
./scripts/setup-minikube.sh
./scripts/build-images.sh
./scripts/deploy.sh
```
