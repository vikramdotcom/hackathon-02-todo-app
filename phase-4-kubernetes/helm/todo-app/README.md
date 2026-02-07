# Todo App Helm Chart

A production-ready Helm chart for deploying the Todo App with AI Chatbot to Kubernetes.

## Overview

This Helm chart deploys a full-stack application consisting of:
- **Frontend**: Next.js 14 application (2 replicas)
- **Backend**: FastAPI application (2 replicas)
- **Database**: PostgreSQL 15 (1 replica with persistent storage)
- **Ingress**: NGINX ingress controller for routing

## Prerequisites

- Kubernetes 1.28+
- Helm 3.12+
- Minikube (for local development)
- Docker images built and available

## Quick Start

### 1. Build Docker Images

```bash
# From phase-4-kubernetes directory
./scripts/build-images.sh
```

### 2. Install the Chart

```bash
helm install todo-app ./helm/todo-app --namespace todo-app --create-namespace
```

### 3. Access the Application

Add to your hosts file:
```
$(minikube ip) todo.local
```

Then visit: http://todo.local

## Configuration

### Values File Structure

The chart uses `values.yaml` for configuration. Key sections:

#### Global Settings

```yaml
global:
  namespace: todo-app
  environment: development
```

#### Frontend Configuration

```yaml
frontend:
  enabled: true
  replicaCount: 2
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: Never
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

#### Backend Configuration

```yaml
backend:
  enabled: true
  replicaCount: 2
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: Never
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

#### Database Configuration

```yaml
database:
  enabled: true
  replicaCount: 1
  persistence:
    enabled: true
    storageClass: standard
    size: 5Gi
```

#### Secrets

**IMPORTANT**: Change these values in production!

```yaml
secrets:
  postgresUser: "postgres"
  postgresPassword: "postgres"  # CHANGE IN PRODUCTION
  secretKey: "your-secret-key-here-change-in-production"  # CHANGE IN PRODUCTION
  openaiApiKey: ""  # Optional - for AI chatbot
```

## Installation Options

### Basic Installation

```bash
helm install todo-app ./helm/todo-app -n todo-app --create-namespace
```

### With Custom Values

```bash
helm install todo-app ./helm/todo-app -n todo-app --create-namespace -f custom-values.yaml
```

### Dry Run (Test)

```bash
helm install todo-app ./helm/todo-app -n todo-app --dry-run --debug
```

### With Specific Values

```bash
helm install todo-app ./helm/todo-app -n todo-app \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=3 \
  --set secrets.openaiApiKey="sk-..."
```

## Upgrading

### Upgrade Existing Release

```bash
helm upgrade todo-app ./helm/todo-app -n todo-app
```

### Upgrade with New Values

```bash
helm upgrade todo-app ./helm/todo-app -n todo-app -f new-values.yaml
```

### Rollback

```bash
# View history
helm history todo-app -n todo-app

# Rollback to previous version
helm rollback todo-app -n todo-app

# Rollback to specific revision
helm rollback todo-app 2 -n todo-app
```

## Uninstallation

```bash
# Uninstall release
helm uninstall todo-app -n todo-app

# Delete namespace (optional)
kubectl delete namespace todo-app
```

## Chart Structure

```
helm/todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── .helmignore            # Files to ignore when packaging
├── templates/
│   ├── _helpers.tpl       # Template helpers
│   ├── NOTES.txt          # Post-installation notes
│   ├── namespace.yaml     # Namespace definition
│   ├── configmap.yaml     # ConfigMap for non-sensitive config
│   ├── secret.yaml        # Secret for sensitive data
│   ├── database-pvc.yaml  # PersistentVolumeClaim for database
│   ├── database-deployment.yaml  # Database deployment
│   ├── database-service.yaml     # Database service
│   ├── backend-deployment.yaml   # Backend deployment
│   ├── backend-service.yaml      # Backend service
│   ├── frontend-deployment.yaml  # Frontend deployment
│   ├── frontend-service.yaml     # Frontend service
│   └── ingress.yaml       # Ingress configuration
└── charts/                # Dependency charts (empty)
```

## Customization

### Environment-Specific Values

Create separate values files for different environments:

**values-dev.yaml**:
```yaml
global:
  environment: development

frontend:
  replicaCount: 1

backend:
  replicaCount: 1

database:
  persistence:
    size: 2Gi
```

**values-prod.yaml**:
```yaml
global:
  environment: production

frontend:
  replicaCount: 3
  image:
    pullPolicy: IfNotPresent

backend:
  replicaCount: 3
  image:
    pullPolicy: IfNotPresent

database:
  persistence:
    size: 20Gi

autoscaling:
  enabled: true
```

Deploy with:
```bash
helm install todo-app ./helm/todo-app -n todo-app -f values-prod.yaml
```

### Enabling Autoscaling

```yaml
autoscaling:
  enabled: true
  frontend:
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 80
  backend:
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 80
```

### Custom Ingress Host

```yaml
ingress:
  enabled: true
  host: myapp.example.com
```

### Disabling Components

```yaml
# Disable frontend (use external frontend)
frontend:
  enabled: false

# Disable database (use external database)
database:
  enabled: false
```

## Validation

### Lint the Chart

```bash
helm lint ./helm/todo-app
```

### Template Rendering

```bash
# Render all templates
helm template todo-app ./helm/todo-app

# Render specific template
helm template todo-app ./helm/todo-app --show-only templates/backend-deployment.yaml
```

### Validate Against Cluster

```bash
helm install todo-app ./helm/todo-app --dry-run --debug
```

## Monitoring

### View Release Status

```bash
helm status todo-app -n todo-app
```

### View Release Values

```bash
helm get values todo-app -n todo-app
```

### View Release Manifest

```bash
helm get manifest todo-app -n todo-app
```

### View Release History

```bash
helm history todo-app -n todo-app
```

## Troubleshooting

### Chart Won't Install

1. **Lint the chart**:
   ```bash
   helm lint ./helm/todo-app
   ```

2. **Check template rendering**:
   ```bash
   helm template todo-app ./helm/todo-app --debug
   ```

3. **Verify values**:
   ```bash
   helm show values ./helm/todo-app
   ```

### Pods Not Starting

1. **Check pod status**:
   ```bash
   kubectl get pods -n todo-app
   ```

2. **Describe pod**:
   ```bash
   kubectl describe pod <pod-name> -n todo-app
   ```

3. **Check logs**:
   ```bash
   kubectl logs <pod-name> -n todo-app
   ```

### Upgrade Fails

1. **Check current release**:
   ```bash
   helm list -n todo-app
   ```

2. **View pending changes**:
   ```bash
   helm upgrade todo-app ./helm/todo-app -n todo-app --dry-run --debug
   ```

3. **Rollback if needed**:
   ```bash
   helm rollback todo-app -n todo-app
   ```

## Best Practices

### Production Deployment

1. **Use external secrets management**:
   - Sealed Secrets
   - External Secrets Operator
   - HashiCorp Vault

2. **Enable resource limits**:
   - Always set requests and limits
   - Monitor actual usage
   - Adjust based on metrics

3. **Enable autoscaling**:
   - Set appropriate min/max replicas
   - Configure CPU/memory targets
   - Test scaling behavior

4. **Use persistent storage**:
   - Enable database persistence
   - Use appropriate storage class
   - Configure backup strategy

5. **Implement monitoring**:
   - Enable ServiceMonitor for Prometheus
   - Configure alerting rules
   - Set up log aggregation

6. **Network policies**:
   - Enable network policies
   - Restrict pod-to-pod communication
   - Allow only necessary traffic

### Security

1. **Change default secrets**:
   ```bash
   helm install todo-app ./helm/todo-app -n todo-app \
     --set secrets.postgresPassword="$(openssl rand -base64 32)" \
     --set secrets.secretKey="$(openssl rand -base64 32)"
   ```

2. **Use image pull secrets** (for private registries):
   ```yaml
   imagePullSecrets:
     - name: regcred
   ```

3. **Run as non-root** (already configured for frontend)

4. **Enable pod security policies**

## Contributing

When modifying the chart:

1. Update version in `Chart.yaml`
2. Document changes in values.yaml comments
3. Test with `helm lint`
4. Test installation with `--dry-run`
5. Update this README

## Support

For issues or questions:
- Check the main README.md
- Review TROUBLESHOOTING.md
- Check Helm documentation: https://helm.sh/docs/

## License

See main project LICENSE file.
