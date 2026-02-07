# Phase IV - Scaling Guide

Complete guide for scaling services and managing resources in the Todo App Kubernetes deployment.

## Table of Contents

1. [Scaling Overview](#scaling-overview)
2. [Manual Scaling](#manual-scaling)
3. [Horizontal Pod Autoscaling (HPA)](#horizontal-pod-autoscaling-hpa)
4. [Resource Management](#resource-management)
5. [Load Testing](#load-testing)
6. [Monitoring](#monitoring)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Scaling Overview

### Why Scale?

- **Handle increased load**: More users, more requests
- **High availability**: Multiple replicas for redundancy
- **Resource optimization**: Scale down during low traffic
- **Performance**: Distribute load across multiple pods

### Scaling Options

| Method | Type | Use Case | Automation |
|--------|------|----------|------------|
| **Manual Scaling** | Horizontal | Quick adjustments, testing | Manual |
| **HPA** | Horizontal | Production, automatic scaling | Automatic |
| **Vertical Scaling** | Vertical | Resource adjustments | Manual |

### Scalable Components

- ✅ **Frontend**: Stateless, can scale freely
- ✅ **Backend**: Stateless, can scale freely
- ❌ **Database**: Stateful, single replica (requires special handling)

---

## Manual Scaling

### Using Helper Script

**Scale Frontend:**
```bash
./scripts/scale-service.sh frontend 3  # Linux/macOS
scripts\scale-service.bat frontend 3   # Windows
```

**Scale Backend:**
```bash
./scripts/scale-service.sh backend 5
```

**Scale Both:**
```bash
./scripts/scale-service.sh all 3
```

### Using kubectl

**Scale Frontend:**
```bash
kubectl scale deployment/frontend --replicas=3 -n todo-app
```

**Scale Backend:**
```bash
kubectl scale deployment/backend --replicas=5 -n todo-app
```

**Verify Scaling:**
```bash
kubectl get deployments -n todo-app
kubectl get pods -n todo-app
```

**Monitor Rollout:**
```bash
kubectl rollout status deployment/frontend -n todo-app
kubectl rollout status deployment/backend -n todo-app
```

### Using Helm

**Scale via Helm Upgrade:**
```bash
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=5
```

**With Values File:**
```yaml
# custom-scale.yaml
frontend:
  replicaCount: 3

backend:
  replicaCount: 5
```

```bash
helm upgrade todo-app ./helm/todo-app -n todo-app -f custom-scale.yaml
```

---

## Horizontal Pod Autoscaling (HPA)

### Overview

HPA automatically scales pods based on CPU/memory utilization or custom metrics.

### Prerequisites

1. **Metrics Server** must be running:
   ```bash
   kubectl get deployment metrics-server -n kube-system
   ```

2. **Resource requests** must be defined (already configured in Helm chart)

### Enable HPA

**Via Helm:**
```bash
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set autoscaling.enabled=true
```

**With Custom Thresholds:**
```bash
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set autoscaling.enabled=true \
  --set autoscaling.frontend.minReplicas=2 \
  --set autoscaling.frontend.maxReplicas=10 \
  --set autoscaling.frontend.targetCPUUtilizationPercentage=70 \
  --set autoscaling.backend.minReplicas=2 \
  --set autoscaling.backend.maxReplicas=10 \
  --set autoscaling.backend.targetCPUUtilizationPercentage=70
```

**Via Values File:**
```yaml
# values-autoscale.yaml
autoscaling:
  enabled: true
  frontend:
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
  backend:
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
```

```bash
helm upgrade todo-app ./helm/todo-app -n todo-app -f values-autoscale.yaml
```

### Monitor HPA

**Check HPA Status:**
```bash
kubectl get hpa -n todo-app
```

**Detailed HPA Info:**
```bash
kubectl describe hpa todo-app-frontend-hpa -n todo-app
kubectl describe hpa todo-app-backend-hpa -n todo-app
```

**Watch HPA in Real-Time:**
```bash
watch kubectl get hpa -n todo-app
```

### HPA Behavior

**Scale Up:**
- Triggers when CPU/memory exceeds target
- Scales up quickly (30 seconds stabilization)
- Can add up to 100% of current pods or 2 pods per 30s

**Scale Down:**
- Triggers when CPU/memory below target
- Scales down slowly (5 minutes stabilization)
- Removes up to 50% of current pods or 1 pod per 60s

### Disable HPA

```bash
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set autoscaling.enabled=false
```

Or delete manually:
```bash
kubectl delete hpa todo-app-frontend-hpa -n todo-app
kubectl delete hpa todo-app-backend-hpa -n todo-app
```

---

## Resource Management

### View Resource Usage

**Pod Resource Usage:**
```bash
kubectl top pods -n todo-app
```

**Node Resource Usage:**
```bash
kubectl top nodes
```

**Detailed Pod Resources:**
```bash
kubectl describe pod <pod-name> -n todo-app | grep -A 5 "Limits\|Requests"
```

### Current Resource Configuration

**Frontend:**
- Requests: 256Mi RAM, 250m CPU
- Limits: 512Mi RAM, 500m CPU

**Backend:**
- Requests: 256Mi RAM, 250m CPU
- Limits: 512Mi RAM, 500m CPU

**Database:**
- Requests: 256Mi RAM, 250m CPU
- Limits: 512Mi RAM, 500m CPU

### Adjust Resource Limits

**Via Helm:**
```bash
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set frontend.resources.requests.memory=512Mi \
  --set frontend.resources.limits.memory=1Gi \
  --set backend.resources.requests.memory=512Mi \
  --set backend.resources.limits.memory=1Gi
```

**Via Values File:**
```yaml
# values-resources.yaml
frontend:
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

backend:
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
```

```bash
helm upgrade todo-app ./helm/todo-app -n todo-app -f values-resources.yaml
```

### Resource Quotas

**Create Namespace Quota:**
```yaml
# resource-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: todo-app-quota
  namespace: todo-app
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
```

```bash
kubectl apply -f resource-quota.yaml
```

**Check Quota Usage:**
```bash
kubectl describe resourcequota todo-app-quota -n todo-app
```

---

## Load Testing

### Generate Load

**Using Apache Bench (ab):**
```bash
# Install ab
sudo apt-get install apache2-utils  # Ubuntu/Debian
brew install apache2  # macOS

# Test frontend
ab -n 1000 -c 10 http://todo.local/

# Test backend API
ab -n 1000 -c 10 http://todo.local/api/health
```

**Using hey:**
```bash
# Install hey
go install github.com/rakyll/hey@latest

# Test with 100 concurrent requests
hey -n 10000 -c 100 http://todo.local/api/health
```

**Using kubectl run:**
```bash
# Create a load generator pod
kubectl run -it --rm load-generator --image=busybox --restart=Never -n todo-app -- /bin/sh

# Inside the pod
while true; do wget -q -O- http://frontend:3000; done
```

### Monitor During Load Test

**Terminal 1 - Watch HPA:**
```bash
watch kubectl get hpa -n todo-app
```

**Terminal 2 - Watch Pods:**
```bash
watch kubectl get pods -n todo-app
```

**Terminal 3 - Watch Resources:**
```bash
watch kubectl top pods -n todo-app
```

**Terminal 4 - Run Load Test:**
```bash
hey -n 100000 -c 100 -q 10 http://todo.local/api/health
```

### Expected Behavior

1. **Initial State**: 2 replicas each (frontend, backend)
2. **Load Increases**: CPU/memory usage rises
3. **HPA Triggers**: When usage exceeds 70-80%
4. **Scale Up**: New pods created (up to max replicas)
5. **Load Distributed**: Requests spread across pods
6. **Load Decreases**: Usage drops
7. **Scale Down**: Excess pods terminated (after 5 min stabilization)

---

## Monitoring

### Real-Time Monitoring

**Dashboard:**
```bash
# Open Kubernetes dashboard
minikube dashboard
```

**Metrics:**
```bash
# Pod metrics
kubectl top pods -n todo-app --sort-by=cpu
kubectl top pods -n todo-app --sort-by=memory

# Node metrics
kubectl top nodes
```

**Events:**
```bash
# Watch events
kubectl get events -n todo-app --sort-by='.lastTimestamp' --watch

# Filter scaling events
kubectl get events -n todo-app | grep -i scale
```

### Logging

**View Logs:**
```bash
# Frontend logs
kubectl logs -f deployment/frontend -n todo-app

# Backend logs
kubectl logs -f deployment/backend -n todo-app

# All pods
kubectl logs -f -l app=todo-app -n todo-app --all-containers=true
```

**Log Aggregation:**
```bash
# Get logs from all replicas
kubectl logs -l component=backend -n todo-app --tail=100

# Follow logs from multiple pods
stern backend -n todo-app  # Requires stern: brew install stern
```

### Alerts

**Set up alerts for:**
- High CPU usage (>80%)
- High memory usage (>80%)
- Pod restarts
- Failed health checks
- HPA scaling events

---

## Best Practices

### 1. Start Conservative

- Begin with 2 replicas
- Monitor actual usage
- Scale based on data, not assumptions

### 2. Set Appropriate Limits

- Requests: What pod needs to run
- Limits: Maximum pod can use
- Ratio: 2:1 (limits:requests) is common

### 3. Use HPA for Production

- Enable HPA for automatic scaling
- Set reasonable min/max replicas
- Monitor and adjust thresholds

### 4. Test Scaling

- Load test before production
- Verify HPA triggers correctly
- Test scale-down behavior

### 5. Monitor Continuously

- Watch resource usage
- Track scaling events
- Set up alerts

### 6. Plan for Peak Load

- Identify peak usage times
- Pre-scale before expected load
- Have capacity buffer

### 7. Database Considerations

- Database doesn't scale horizontally easily
- Consider read replicas for read-heavy workloads
- Use connection pooling
- Monitor database connections

---

## Troubleshooting

### HPA Not Scaling

**Check Metrics Server:**
```bash
kubectl get deployment metrics-server -n kube-system
kubectl logs -n kube-system deployment/metrics-server
```

**Check Resource Requests:**
```bash
kubectl describe deployment frontend -n todo-app | grep -A 5 "Requests"
```

**Check HPA Status:**
```bash
kubectl describe hpa todo-app-frontend-hpa -n todo-app
```

**Common Issues:**
- Metrics server not running
- Resource requests not defined
- Target utilization too high
- Not enough load to trigger scaling

### Pods Not Starting After Scale

**Check Events:**
```bash
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

**Check Pod Status:**
```bash
kubectl describe pod <pod-name> -n todo-app
```

**Common Issues:**
- Insufficient cluster resources
- Image pull errors
- Resource quota exceeded
- Node capacity reached

### High Resource Usage

**Identify Resource Hogs:**
```bash
kubectl top pods -n todo-app --sort-by=memory
kubectl top pods -n todo-app --sort-by=cpu
```

**Check Logs for Errors:**
```bash
kubectl logs <pod-name> -n todo-app
```

**Solutions:**
- Increase resource limits
- Optimize application code
- Add more replicas
- Investigate memory leaks

### Uneven Load Distribution

**Check Service Endpoints:**
```bash
kubectl get endpoints -n todo-app
```

**Check Pod Readiness:**
```bash
kubectl get pods -n todo-app -o wide
```

**Solutions:**
- Verify readiness probes
- Check pod health
- Restart unhealthy pods

---

## Scaling Scenarios

### Scenario 1: Anticipated Traffic Spike

**Before Event:**
```bash
# Scale up proactively
./scripts/scale-service.sh all 5

# Or enable HPA with higher min replicas
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set autoscaling.enabled=true \
  --set autoscaling.frontend.minReplicas=5 \
  --set autoscaling.backend.minReplicas=5
```

**After Event:**
```bash
# Scale down
./scripts/scale-service.sh all 2

# Or adjust HPA
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set autoscaling.frontend.minReplicas=2 \
  --set autoscaling.backend.minReplicas=2
```

### Scenario 2: Development/Testing

**Development (Minimal Resources):**
```bash
helm upgrade todo-app ./helm/todo-app -n todo-app -f helm/todo-app/values-dev.yaml
# 1 replica each, reduced resources
```

**Testing (Production-like):**
```bash
helm upgrade todo-app ./helm/todo-app -n todo-app -f helm/todo-app/values-test.yaml
# 2 replicas each, standard resources
```

### Scenario 3: Cost Optimization

**Off-Peak Hours:**
```bash
# Scale down to minimum
./scripts/scale-service.sh all 1
```

**Peak Hours:**
```bash
# Scale up
./scripts/scale-service.sh all 3
```

**Or use HPA** to handle this automatically.

---

## Additional Resources

- **Kubernetes HPA Documentation**: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- **Resource Management**: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- **Metrics Server**: https://github.com/kubernetes-sigs/metrics-server

---

**Last Updated**: February 7, 2026
