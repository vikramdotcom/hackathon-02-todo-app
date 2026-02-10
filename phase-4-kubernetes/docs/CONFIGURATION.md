# Configuration Management Guide

**Phase IV - User Story 5: Configuration Management**

This guide covers managing environment-specific configurations, secrets, and ConfigMaps for the Todo App Kubernetes deployment.

---

## Table of Contents

1. [Overview](#overview)
2. [Configuration Profiles](#configuration-profiles)
3. [Environment Variables](#environment-variables)
4. [Secrets Management](#secrets-management)
5. [ConfigMap Management](#configmap-management)
6. [Secret Rotation](#secret-rotation)
7. [Configuration Updates](#configuration-updates)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The Todo App uses a layered configuration approach:

1. **Base Configuration**: Default values in `values.yaml`
2. **Environment Profiles**: Environment-specific overrides (`values-dev.yaml`, `values-test.yaml`)
3. **Secrets**: Sensitive data stored in Kubernetes Secrets
4. **ConfigMaps**: Non-sensitive configuration data
5. **Environment Variables**: Runtime configuration via `.env` file

### Configuration Hierarchy

```
.env file (local development)
    ↓
values.yaml (base defaults)
    ↓
values-{env}.yaml (environment overrides)
    ↓
Kubernetes Secrets (sensitive data)
    ↓
Kubernetes ConfigMaps (application config)
```

---

## Configuration Profiles

### Available Profiles

#### Development Profile (`values-dev.yaml`)

**Purpose**: Local development with minimal resources

**Characteristics**:
- Single replica per service
- Reduced memory limits (128Mi-256Mi)
- Debug logging enabled
- Autoscaling disabled
- Suitable for laptop/desktop development

**Usage**:
```bash
# Linux/macOS
./scripts/helm-deploy.sh -f values-dev.yaml

# Windows
scripts\helm-deploy.bat -f values-dev.yaml
```

#### Testing Profile (`values-test.yaml`)

**Purpose**: Production-like testing environment

**Characteristics**:
- Multiple replicas (2 per service)
- Standard resource limits (256Mi-512Mi)
- Info-level logging
- Autoscaling enabled
- Pod disruption budgets enabled
- Suitable for integration testing

**Usage**:
```bash
# Linux/macOS
./scripts/helm-deploy.sh -f values-test.yaml

# Windows
scripts\helm-deploy.bat -f values-test.yaml
```

#### Production Profile (Future)

**Purpose**: Production deployment (not yet implemented)

**Planned Characteristics**:
- High availability (3+ replicas)
- Production resource limits
- Error-level logging
- Autoscaling with conservative thresholds
- Network policies enabled
- Resource quotas enforced

### Creating Custom Profiles

1. Copy an existing profile:
```bash
cp helm/todo-app/values-dev.yaml helm/todo-app/values-custom.yaml
```

2. Modify the values:
```yaml
# values-custom.yaml
global:
  environment: custom

frontend:
  replicaCount: 2
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

3. Deploy with custom profile:
```bash
./scripts/helm-deploy.sh -f values-custom.yaml
```

---

## Environment Variables

### Local Development (.env file)

The `.env.example` file contains all available environment variables with documentation.

**Setup**:
```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env  # or vim, code, etc.
```

**Key Variables**:

```bash
# Backend Configuration
BACKEND_PORT=8000
DATABASE_URL=postgresql://postgres:password@database:5432/todo_db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_APP_NAME="Todo App"

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=todo_db

# Kubernetes Configuration
NAMESPACE=todo-app
INGRESS_HOST=todo.local
```

### Kubernetes Environment Variables

Environment variables are injected into pods via:

1. **ConfigMaps** (non-sensitive):
```yaml
envFrom:
  - configMapRef:
      name: todo-app-config
```

2. **Secrets** (sensitive):
```yaml
envFrom:
  - secretRef:
      name: todo-app-secrets
```

3. **Direct values** (from Helm values):
```yaml
env:
  - name: ENVIRONMENT
    value: {{ .Values.global.environment }}
```

---

## Secrets Management

### Creating Secrets

#### Method 1: Using Helper Script (Recommended)

```bash
# Linux/macOS
./scripts/manage-secrets.sh create

# Windows
scripts\manage-secrets.bat create
```

This will prompt for all required secret values.

#### Method 2: Manual Creation

```bash
# Create from literal values
kubectl create secret generic todo-app-secrets \
  -n todo-app \
  --from-literal=DATABASE_URL=postgresql://user:pass@host:5432/db \
  --from-literal=SECRET_KEY=your-secret-key \
  --from-literal=OPENAI_API_KEY=your-api-key

# Create from .env file
kubectl create secret generic todo-app-secrets \
  -n todo-app \
  --from-env-file=.env
```

#### Method 3: Using Helm

Secrets are automatically created during Helm deployment from values:

```yaml
# values.yaml
secrets:
  databaseUrl: "postgresql://postgres:password@database:5432/todo_db"
  secretKey: "change-me-in-production"
  openaiApiKey: ""
```

**⚠️ WARNING**: Never commit actual secrets to version control!

### Viewing Secrets

```bash
# List secrets
kubectl get secrets -n todo-app

# View secret details (base64 encoded)
kubectl get secret todo-app-secrets -n todo-app -o yaml

# Decode secret value
kubectl get secret todo-app-secrets -n todo-app \
  -o jsonpath='{.data.SECRET_KEY}' | base64 --decode
```

### Updating Secrets

```bash
# Using helper script
./scripts/manage-secrets.sh update

# Manual update
kubectl create secret generic todo-app-secrets \
  -n todo-app \
  --from-literal=SECRET_KEY=new-secret-key \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new secrets
kubectl rollout restart deployment/backend -n todo-app
```

### Deleting Secrets

```bash
# Using helper script
./scripts/manage-secrets.sh delete

# Manual deletion
kubectl delete secret todo-app-secrets -n todo-app
```

---

## ConfigMap Management

### Creating ConfigMaps

ConfigMaps store non-sensitive configuration data.

#### Method 1: Using Helm (Recommended)

ConfigMaps are automatically created from `values.yaml`:

```yaml
# values.yaml
config:
  backend:
    logLevel: "info"
    corsOrigins: "http://localhost:3000"
  frontend:
    apiUrl: "http://backend:8000"
    appName: "Todo App"
```

#### Method 2: Manual Creation

```bash
# From literal values
kubectl create configmap todo-app-config \
  -n todo-app \
  --from-literal=LOG_LEVEL=info \
  --from-literal=CORS_ORIGINS=http://localhost:3000

# From file
kubectl create configmap todo-app-config \
  -n todo-app \
  --from-file=config.json
```

### Viewing ConfigMaps

```bash
# List ConfigMaps
kubectl get configmaps -n todo-app

# View ConfigMap details
kubectl get configmap todo-app-config -n todo-app -o yaml

# View specific key
kubectl get configmap todo-app-config -n todo-app \
  -o jsonpath='{.data.LOG_LEVEL}'
```

### Updating ConfigMaps

#### Example 1: Update Log Level

```bash
# Get current ConfigMap
kubectl get configmap todo-app-config -n todo-app -o yaml > configmap.yaml

# Edit the file
# Change LOG_LEVEL: "info" to LOG_LEVEL: "debug"

# Apply changes
kubectl apply -f configmap.yaml

# Restart pods to pick up changes
kubectl rollout restart deployment/backend -n todo-app
kubectl rollout restart deployment/frontend -n todo-app
```

#### Example 2: Update via Helm

```bash
# Update values.yaml
# config:
#   backend:
#     logLevel: "debug"

# Upgrade Helm release
helm upgrade todo-app ./helm/todo-app -n todo-app

# Pods will automatically restart with new config
```

#### Example 3: Patch ConfigMap

```bash
# Patch specific key
kubectl patch configmap todo-app-config -n todo-app \
  --type merge \
  -p '{"data":{"LOG_LEVEL":"debug"}}'

# Restart pods
kubectl rollout restart deployment/backend -n todo-app
```

### ConfigMap Best Practices

1. **Separate Concerns**: Use different ConfigMaps for different components
2. **Version Control**: Keep ConfigMap definitions in Git
3. **Immutable ConfigMaps**: Consider using immutable ConfigMaps for production
4. **Size Limits**: ConfigMaps are limited to 1MB
5. **Restart Required**: Pods must be restarted to pick up ConfigMap changes

---

## Secret Rotation

### Why Rotate Secrets?

- Security best practice
- Compliance requirements
- Suspected compromise
- Regular maintenance

### Rotation Procedures

#### 1. Database Password Rotation

```bash
# Step 1: Update database password
kubectl exec -it deployment/database -n todo-app -- \
  psql -U postgres -c "ALTER USER postgres PASSWORD 'new-password';"

# Step 2: Update secret
kubectl create secret generic todo-app-secrets \
  -n todo-app \
  --from-literal=DATABASE_URL=postgresql://postgres:new-password@database:5432/todo_db \
  --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Restart backend pods
kubectl rollout restart deployment/backend -n todo-app

# Step 4: Verify connectivity
kubectl logs deployment/backend -n todo-app --tail=50
```

#### 2. API Key Rotation (OpenAI)

```bash
# Step 1: Generate new API key in OpenAI dashboard

# Step 2: Update secret
./scripts/manage-secrets.sh update
# Enter new OPENAI_API_KEY when prompted

# Step 3: Restart backend pods
kubectl rollout restart deployment/backend -n todo-app

# Step 4: Test API functionality
kubectl exec -it deployment/backend -n todo-app -- \
  curl -s http://localhost:8000/health
```

#### 3. Application Secret Key Rotation

```bash
# Step 1: Generate new secret key
NEW_SECRET=$(openssl rand -hex 32)

# Step 2: Update secret
kubectl create secret generic todo-app-secrets \
  -n todo-app \
  --from-literal=SECRET_KEY=$NEW_SECRET \
  --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Restart backend pods
kubectl rollout restart deployment/backend -n todo-app

# Step 4: Verify application functionality
# Note: This will invalidate existing sessions
```

### Rotation Checklist

- [ ] Backup current secrets
- [ ] Generate new credentials
- [ ] Update secrets in Kubernetes
- [ ] Restart affected pods
- [ ] Verify application functionality
- [ ] Monitor for errors
- [ ] Update documentation
- [ ] Revoke old credentials (if applicable)

### Automated Rotation (Future Enhancement)

Consider implementing automated secret rotation using:
- **External Secrets Operator**: Sync secrets from external vaults
- **Sealed Secrets**: Encrypt secrets in Git
- **Vault**: HashiCorp Vault integration
- **AWS Secrets Manager**: For cloud deployments

---

## Configuration Updates

### Zero-Downtime Configuration Updates

#### Strategy 1: Rolling Update

```bash
# Update configuration in values.yaml
# Then upgrade Helm release
helm upgrade todo-app ./helm/todo-app -n todo-app

# Helm will perform rolling update automatically
# Old pods remain until new pods are ready
```

#### Strategy 2: Blue-Green Deployment

```bash
# Deploy new version with different release name
helm install todo-app-v2 ./helm/todo-app -n todo-app \
  -f values-new.yaml

# Test new version
kubectl port-forward svc/todo-app-v2-frontend 3001:3000 -n todo-app

# Switch traffic (update Ingress)
kubectl patch ingress todo-app-ingress -n todo-app \
  --type merge \
  -p '{"spec":{"rules":[{"host":"todo.local","http":{"paths":[{"path":"/","pathType":"Prefix","backend":{"service":{"name":"todo-app-v2-frontend","port":{"number":3000}}}}]}}]}}'

# Delete old version
helm uninstall todo-app -n todo-app
```

#### Strategy 3: Canary Deployment

```bash
# Deploy canary version with 1 replica
helm install todo-app-canary ./helm/todo-app -n todo-app \
  -f values-canary.yaml \
  --set frontend.replicaCount=1

# Monitor metrics and errors
kubectl top pods -n todo-app
kubectl logs -l app=todo-app-canary -n todo-app

# If successful, scale up canary and scale down old version
kubectl scale deployment/todo-app-canary-frontend --replicas=3 -n todo-app
kubectl scale deployment/todo-app-frontend --replicas=0 -n todo-app
```

### Configuration Validation

Before applying configuration changes:

```bash
# Validate Helm chart
helm lint ./helm/todo-app

# Dry-run deployment
helm upgrade todo-app ./helm/todo-app -n todo-app --dry-run

# Validate Kubernetes manifests
kubectl apply --dry-run=client -f k8s/

# Check for syntax errors
yamllint helm/todo-app/values.yaml
```

---

## Best Practices

### 1. Separation of Concerns

```yaml
# ✅ Good: Separate secrets and config
secrets:
  databaseUrl: "..."
  apiKey: "..."

config:
  logLevel: "info"
  corsOrigins: "..."

# ❌ Bad: Mixing secrets and config
config:
  logLevel: "info"
  databasePassword: "password123"  # Should be in secrets!
```

### 2. Environment-Specific Values

```yaml
# ✅ Good: Use environment profiles
# values-dev.yaml
global:
  environment: development
frontend:
  replicaCount: 1

# values-prod.yaml
global:
  environment: production
frontend:
  replicaCount: 3

# ❌ Bad: Hardcoding environment-specific values in base
frontend:
  replicaCount: 1  # Always 1, even in production
```

### 3. Secret Management

```bash
# ✅ Good: Use secret management tools
./scripts/manage-secrets.sh create

# ✅ Good: Use environment variables
export DATABASE_PASSWORD=$(kubectl get secret ...)

# ❌ Bad: Hardcoding secrets
kubectl create secret generic app-secrets \
  --from-literal=password=password123  # Visible in shell history!

# ❌ Bad: Committing secrets to Git
git add .env  # Contains actual secrets
```

### 4. Configuration Versioning

```bash
# ✅ Good: Version configuration with code
git add helm/todo-app/values-dev.yaml
git commit -m "Update dev environment resources"

# ✅ Good: Tag configuration releases
git tag -a config-v1.2.0 -m "Production config for v1.2.0"

# ❌ Bad: Manual configuration changes without tracking
kubectl edit configmap todo-app-config  # Changes not in Git
```

### 5. Documentation

```yaml
# ✅ Good: Document configuration options
# values.yaml
frontend:
  # Number of frontend replicas
  # Dev: 1, Test: 2, Prod: 3+
  replicaCount: 1

  # Resource limits
  # Adjust based on load testing results
  resources:
    requests:
      memory: "128Mi"  # Minimum required
      cpu: "100m"      # Minimum required

# ❌ Bad: Undocumented magic numbers
frontend:
  replicaCount: 1
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
```

---

## Troubleshooting

### Issue: Pods Not Picking Up Configuration Changes

**Symptoms**:
- ConfigMap updated but pods still use old values
- Secret rotated but application still uses old credentials

**Solution**:
```bash
# Restart pods to pick up changes
kubectl rollout restart deployment/backend -n todo-app
kubectl rollout restart deployment/frontend -n todo-app

# Verify rollout completed
kubectl rollout status deployment/backend -n todo-app
```

### Issue: Secret Not Found

**Symptoms**:
```
Error: secret "todo-app-secrets" not found
```

**Solution**:
```bash
# Check if secret exists
kubectl get secrets -n todo-app

# Create secret if missing
./scripts/manage-secrets.sh create

# Verify secret created
kubectl get secret todo-app-secrets -n todo-app
```

### Issue: Invalid Configuration Values

**Symptoms**:
- Pods in CrashLoopBackOff
- Application errors in logs

**Solution**:
```bash
# Check pod logs for configuration errors
kubectl logs deployment/backend -n todo-app --tail=100

# Validate configuration
helm lint ./helm/todo-app

# Check ConfigMap values
kubectl get configmap todo-app-config -n todo-app -o yaml

# Rollback to previous configuration
helm rollback todo-app -n todo-app
```

### Issue: Configuration Profile Not Applied

**Symptoms**:
- Deployment uses default values instead of profile values

**Solution**:
```bash
# Verify profile file exists
ls helm/todo-app/values-dev.yaml

# Deploy with explicit profile
helm upgrade todo-app ./helm/todo-app -n todo-app \
  -f helm/todo-app/values-dev.yaml

# Verify values applied
helm get values todo-app -n todo-app
```

### Issue: Secret Rotation Breaks Application

**Symptoms**:
- Application cannot connect to database after rotation
- Authentication errors in logs

**Solution**:
```bash
# Verify secret updated correctly
kubectl get secret todo-app-secrets -n todo-app -o yaml

# Check if pods restarted
kubectl get pods -n todo-app

# Force restart if needed
kubectl rollout restart deployment/backend -n todo-app

# Test connectivity
kubectl exec -it deployment/backend -n todo-app -- \
  curl -s http://localhost:8000/health
```

---

## Additional Resources

- [Kubernetes Secrets Documentation](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Kubernetes ConfigMaps Documentation](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Helm Values Files](https://helm.sh/docs/chart_template_guide/values_files/)
- [12-Factor App Configuration](https://12factor.net/config)

---

## Quick Reference

### Common Commands

```bash
# View current configuration
helm get values todo-app -n todo-app

# Update configuration
helm upgrade todo-app ./helm/todo-app -n todo-app -f values-dev.yaml

# Manage secrets
./scripts/manage-secrets.sh create|update|delete|view

# View ConfigMaps
kubectl get configmap -n todo-app

# Restart pods
kubectl rollout restart deployment/backend -n todo-app

# Rollback changes
helm rollback todo-app -n todo-app
```

### Configuration Files

- `helm/todo-app/values.yaml` - Base configuration
- `helm/todo-app/values-dev.yaml` - Development profile
- `helm/todo-app/values-test.yaml` - Testing profile
- `.env.example` - Environment variable template
- `docs/CONFIGURATION.md` - This guide

---

**Last Updated**: February 7, 2026
**Phase**: IV - Local Kubernetes Deployment
**User Story**: US5 - Configuration Management
