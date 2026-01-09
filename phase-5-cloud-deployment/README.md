# Phase V: Advanced Cloud Deployment

**Status**: 🔜 Planned
**Points**: 300
**Due Date**: Jan 18, 2026
**Technology Stack**: Apache Kafka, Dapr, DigitalOcean Kubernetes (DOKS)

## Overview

Phase V deploys the todo application to production cloud infrastructure with enterprise-grade features including event streaming, microservices architecture, distributed tracing, and advanced observability. This phase represents a production-ready, scalable deployment.

## Planned Features

### Event-Driven Architecture (Kafka)
- 🔜 Apache Kafka cluster for event streaming
- 🔜 Event sourcing for todo operations
- 🔜 CQRS (Command Query Responsibility Segregation)
- 🔜 Event replay and time-travel debugging
- 🔜 Dead letter queues for failed events
- 🔜 Schema registry for event validation
- 🔜 Kafka Connect for data integration

### Microservices with Dapr
- 🔜 Service-to-service invocation
- 🔜 State management with Dapr
- 🔜 Pub/Sub messaging
- 🔜 Distributed tracing
- 🔜 Secret management
- 🔜 Actor pattern implementation
- 🔜 Observability and monitoring

### DigitalOcean Kubernetes (DOKS)
- 🔜 Managed Kubernetes cluster
- 🔜 Auto-scaling node pools
- 🔜 Load balancer integration
- 🔜 Block storage volumes
- 🔜 Container registry
- 🔜 VPC networking
- 🔜 Firewall rules and security

### Production Features
- 🔜 Multi-region deployment
- 🔜 Blue-green deployments
- 🔜 Canary releases
- 🔜 Circuit breakers and retries
- 🔜 Rate limiting and throttling
- 🔜 API gateway (Kong/Ambassador)
- 🔜 CDN integration

### Advanced Observability
- 🔜 Distributed tracing (Jaeger/Tempo)
- 🔜 Centralized logging (Loki/ELK)
- 🔜 Metrics and dashboards (Prometheus/Grafana)
- 🔜 APM (Application Performance Monitoring)
- 🔜 Error tracking (Sentry)
- 🔜 Uptime monitoring
- 🔜 Cost monitoring and optimization

### Security & Compliance
- 🔜 TLS/SSL certificates (Let's Encrypt)
- 🔜 OAuth2/OIDC authentication
- 🔜 RBAC (Role-Based Access Control)
- 🔜 Network policies
- 🔜 Pod security policies
- 🔜 Secrets encryption at rest
- 🔜 Audit logging
- 🔜 Vulnerability scanning

## Architecture

```
phase-5-cloud-deployment/
├── infrastructure/
│   ├── terraform/              # Infrastructure as Code
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── modules/
│   │   │   ├── doks/
│   │   │   ├── kafka/
│   │   │   ├── networking/
│   │   │   └── monitoring/
│   │   └── environments/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── prod/
│   └── pulumi/                 # Alternative IaC
│       └── index.ts
├── kafka/
│   ├── topics/
│   │   ├── todo-events.yaml
│   │   ├── user-events.yaml
│   │   └── notification-events.yaml
│   ├── schemas/
│   │   ├── todo-created.avsc
│   │   ├── todo-updated.avsc
│   │   └── todo-deleted.avsc
│   ├── connectors/
│   │   ├── postgres-source.json
│   │   └── elasticsearch-sink.json
│   └── streams/
│       └── todo-aggregator.py
├── dapr/
│   ├── components/
│   │   ├── pubsub.yaml
│   │   ├── statestore.yaml
│   │   ├── secrets.yaml
│   │   └── bindings.yaml
│   ├── configuration/
│   │   ├── tracing.yaml
│   │   ├── middleware.yaml
│   │   └── resiliency.yaml
│   └── actors/
│       └── todo-actor.py
├── services/
│   ├── command-service/        # Write operations
│   │   ├── Dockerfile
│   │   ├── app/
│   │   └── dapr.yaml
│   ├── query-service/          # Read operations
│   │   ├── Dockerfile
│   │   ├── app/
│   │   └── dapr.yaml
│   ├── event-processor/        # Event handling
│   │   ├── Dockerfile
│   │   ├── app/
│   │   └── dapr.yaml
│   └── notification-service/   # Notifications
│       ├── Dockerfile
│       ├── app/
│       └── dapr.yaml
├── k8s/
│   ├── base/
│   │   ├── kafka/
│   │   ├── dapr/
│   │   ├── services/
│   │   └── monitoring/
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── prod/
├── monitoring/
│   ├── grafana/
│   │   └── dashboards/
│   │       ├── kafka-metrics.json
│   │       ├── dapr-metrics.json
│   │       └── business-metrics.json
│   ├── prometheus/
│   │   ├── rules/
│   │   └── alerts/
│   └── jaeger/
│       └── config.yaml
├── scripts/
│   ├── setup-doks.sh
│   ├── deploy-kafka.sh
│   ├── deploy-dapr.sh
│   ├── deploy-services.sh
│   └── backup-restore.sh
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   ├── runbook.md
│   └── disaster-recovery.md
└── README.md                   # This file
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Cloud Provider | DigitalOcean | Managed Kubernetes and infrastructure |
| Orchestration | DOKS (Kubernetes) | Container orchestration |
| Event Streaming | Apache Kafka | Event-driven architecture |
| Microservices | Dapr | Service mesh and runtime |
| IaC | Terraform/Pulumi | Infrastructure as Code |
| API Gateway | Kong/Ambassador | API management |
| Service Mesh | Istio/Linkerd | Traffic management |
| Tracing | Jaeger/Tempo | Distributed tracing |
| Logging | Loki/ELK | Centralized logging |
| Metrics | Prometheus/Grafana | Monitoring and alerting |
| APM | Datadog/New Relic | Application performance |
| CDN | Cloudflare | Content delivery |
| DNS | DigitalOcean DNS | Domain management |
| Certificates | Let's Encrypt | TLS/SSL automation |

## Event-Driven Architecture

### Kafka Topics

**todo-events**
- `todo.created` - New todo created
- `todo.updated` - Todo modified
- `todo.deleted` - Todo removed
- `todo.completed` - Todo marked complete

**user-events**
- `user.registered` - New user signup
- `user.login` - User authentication
- `user.updated` - Profile changes

**notification-events**
- `notification.email` - Email notifications
- `notification.push` - Push notifications
- `notification.sms` - SMS notifications

### Event Schema Example

```json
{
  "type": "record",
  "name": "TodoCreated",
  "namespace": "com.todoapp.events",
  "fields": [
    {"name": "event_id", "type": "string"},
    {"name": "timestamp", "type": "long"},
    {"name": "user_id", "type": "int"},
    {"name": "todo_id", "type": "int"},
    {"name": "title", "type": "string"},
    {"name": "priority", "type": "string"},
    {"name": "due_date", "type": ["null", "long"]},
    {"name": "tags", "type": {"type": "array", "items": "string"}}
  ]
}
```

### CQRS Pattern

**Command Service** (Write)
- Handles create, update, delete operations
- Publishes events to Kafka
- Validates business rules
- Returns command results

**Query Service** (Read)
- Handles read operations
- Consumes events from Kafka
- Maintains read-optimized views
- Supports complex queries

**Event Processor**
- Consumes events from Kafka
- Updates read models
- Triggers side effects
- Handles event replay

## Dapr Integration

### Service Invocation
```python
# Command service calling query service
from dapr.clients import DaprClient

with DaprClient() as client:
    result = client.invoke_method(
        app_id='query-service',
        method_name='get-todos',
        data=json.dumps({'user_id': 123})
    )
```

### Pub/Sub
```python
# Publishing events
from dapr.clients import DaprClient

with DaprClient() as client:
    client.publish_event(
        pubsub_name='kafka-pubsub',
        topic_name='todo-events',
        data=json.dumps(event_data)
    )
```

### State Management
```python
# Storing state with Dapr
from dapr.clients import DaprClient

with DaprClient() as client:
    client.save_state(
        store_name='redis-state',
        key=f'todo-{todo_id}',
        value=json.dumps(todo_data)
    )
```

### Actor Pattern
```python
# Todo Actor for stateful operations
from dapr.actor import Actor, ActorMethod

class TodoActor(Actor):
    async def _on_activate(self):
        self.todo_data = await self._state_manager.try_get_state('todo')

    @ActorMethod(name="UpdateTodo")
    async def update_todo(self, data: dict):
        self.todo_data.update(data)
        await self._state_manager.set_state('todo', self.todo_data)
        await self._state_manager.save_state()
```

## Infrastructure as Code

### Terraform Example

```hcl
# main.tf
resource "digitalocean_kubernetes_cluster" "todo_app" {
  name    = "todo-app-prod"
  region  = "nyc1"
  version = "1.28.2-do.0"

  node_pool {
    name       = "worker-pool"
    size       = "s-4vcpu-8gb"
    auto_scale = true
    min_nodes  = 3
    max_nodes  = 10
  }

  tags = ["production", "todo-app"]
}

resource "digitalocean_database_cluster" "postgres" {
  name       = "todo-db-prod"
  engine     = "pg"
  version    = "15"
  size       = "db-s-4vcpu-8gb"
  region     = "nyc1"
  node_count = 3
}

resource "digitalocean_loadbalancer" "public" {
  name   = "todo-app-lb"
  region = "nyc1"

  forwarding_rule {
    entry_port     = 443
    entry_protocol = "https"
    target_port    = 80
    target_protocol = "http"
    certificate_id = digitalocean_certificate.cert.id
  }

  healthcheck {
    port     = 80
    protocol = "http"
    path     = "/health"
  }

  droplet_tag = "todo-app"
}
```

## Deployment Strategy

### Blue-Green Deployment
```yaml
# Blue deployment (current)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend-blue
  labels:
    version: blue
spec:
  replicas: 5
  selector:
    matchLabels:
      app: todo-backend
      version: blue

---
# Green deployment (new)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend-green
  labels:
    version: green
spec:
  replicas: 5
  selector:
    matchLabels:
      app: todo-backend
      version: green

---
# Service switches between blue and green
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
spec:
  selector:
    app: todo-backend
    version: blue  # Switch to 'green' for deployment
```

### Canary Release
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: todo-backend
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todo-backend
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
    - name: request-duration
      thresholdRange:
        max: 500
```

## Monitoring & Observability

### Grafana Dashboards
- **Business Metrics**: Todos created/completed, active users, conversion rates
- **Kafka Metrics**: Throughput, lag, consumer group status
- **Dapr Metrics**: Service invocations, pub/sub latency, state operations
- **Infrastructure**: CPU, memory, disk, network usage
- **Cost Metrics**: Resource costs, optimization opportunities

### Prometheus Alerts
```yaml
groups:
- name: todo-app-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"

  - alert: KafkaConsumerLag
    expr: kafka_consumer_lag > 1000
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Kafka consumer lag is high"
```

## Development Roadmap

### Phase 5.1: Infrastructure Setup
- [ ] Setup DigitalOcean account
- [ ] Create DOKS cluster
- [ ] Configure networking and VPC
- [ ] Setup managed databases
- [ ] Configure DNS and load balancers

### Phase 5.2: Kafka Deployment
- [ ] Deploy Kafka cluster
- [ ] Create topics and schemas
- [ ] Setup Kafka Connect
- [ ] Configure monitoring
- [ ] Test event streaming

### Phase 5.3: Dapr Integration
- [ ] Install Dapr on DOKS
- [ ] Configure components
- [ ] Implement service invocation
- [ ] Setup pub/sub
- [ ] Add state management

### Phase 5.4: Microservices Migration
- [ ] Split monolith into services
- [ ] Implement CQRS pattern
- [ ] Deploy command service
- [ ] Deploy query service
- [ ] Deploy event processor

### Phase 5.5: Production Features
- [ ] Setup API gateway
- [ ] Implement circuit breakers
- [ ] Add rate limiting
- [ ] Configure CDN
- [ ] Setup SSL/TLS

### Phase 5.6: Observability
- [ ] Deploy monitoring stack
- [ ] Create dashboards
- [ ] Setup alerting
- [ ] Implement tracing
- [ ] Add APM

### Phase 5.7: Security & Compliance
- [ ] Implement OAuth2/OIDC
- [ ] Configure RBAC
- [ ] Setup network policies
- [ ] Enable audit logging
- [ ] Run security scans

## Prerequisites

- DigitalOcean account with billing enabled
- Domain name for the application
- Terraform or Pulumi installed
- kubectl and doctl CLI tools
- Helm 3+
- Dapr CLI

## Getting Started (Coming Soon)

```bash
# Setup DigitalOcean CLI
doctl auth init

# Create infrastructure with Terraform
cd infrastructure/terraform/environments/prod
terraform init
terraform plan
terraform apply

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-app-prod

# Deploy Kafka
./scripts/deploy-kafka.sh

# Deploy Dapr
./scripts/deploy-dapr.sh

# Deploy services
./scripts/deploy-services.sh

# Access application
kubectl get ingress -n todo-app
```

## Cost Estimation

### Monthly Costs (Production)

| Resource | Specification | Monthly Cost |
|----------|--------------|--------------|
| DOKS Cluster | 3x s-4vcpu-8gb nodes | ~$144 |
| Managed PostgreSQL | 3-node HA cluster | ~$180 |
| Load Balancer | 1x load balancer | ~$12 |
| Block Storage | 500GB SSD | ~$50 |
| Container Registry | 500GB storage | ~$5 |
| Kafka (self-hosted) | 3x s-4vcpu-8gb nodes | ~$144 |
| Monitoring | Grafana Cloud | ~$50 |
| CDN | Cloudflare Pro | ~$20 |
| **Total** | | **~$605/month** |

## Migration from Phase IV

The Phase IV Kubernetes deployment will be migrated to:
- Minikube → DigitalOcean Kubernetes (DOKS)
- Local storage → Managed databases
- Single cluster → Multi-region deployment
- Basic monitoring → Enterprise observability

## Status

🔜 **Not Started** - Waiting for Phase IV completion and approval.

---

**Previous Phase**: [Phase IV - Kubernetes](../phase-4-kubernetes/README.md)

## Additional Resources

- [DigitalOcean Kubernetes Documentation](https://docs.digitalocean.com/products/kubernetes/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Dapr Documentation](https://docs.dapr.io/)
- [Terraform DigitalOcean Provider](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs)
