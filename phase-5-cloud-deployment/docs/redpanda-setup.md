# Redpanda Cloud Setup Guide

## Overview
This guide covers setting up Redpanda Cloud for Phase V event-driven architecture.

## Prerequisites
- Redpanda Cloud account (free serverless tier)
- kubectl configured for your cluster
- Kubernetes secrets management

## Step 1: Sign Up for Redpanda Cloud (T009)

1. Visit https://redpanda.com/cloud
2. Sign up for free serverless tier
3. Create a new cluster:
   - Name: `todo-app-events`
   - Region: Choose closest to your DOKS cluster
   - Tier: Serverless (free tier)

## Step 2: Create Topics (T010)

Create three topics for event-driven architecture:

```bash
# Using Redpanda Cloud Console or CLI
rpk topic create task-events --partitions 3 --replicas 3
rpk topic create reminders --partitions 3 --replicas 3
rpk topic create task-updates --partitions 3 --replicas 3
```

**Topic Configuration**:
- `task-events`: All CRUD operations (created, updated, completed, deleted)
- `reminders`: Reminder scheduling and triggering
- `task-updates`: Real-time UI updates

## Step 3: Configure SASL Authentication (T011)

1. In Redpanda Cloud Console, create a new user:
   - Username: `todo-app-service`
   - Permissions: Read/Write on all topics

2. Save credentials securely:
   ```bash
   # Create Kubernetes secret
   kubectl create secret generic redpanda-credentials \
     --from-literal=bootstrap-servers='<YOUR_BOOTSTRAP_SERVERS>' \
     --from-literal=sasl-username='<YOUR_USERNAME>' \
     --from-literal=sasl-password='<YOUR_PASSWORD>' \
     --namespace=todo-app
   ```

3. Store in `.env` for local development:
   ```env
   REDPANDA_BOOTSTRAP_SERVERS=<YOUR_BOOTSTRAP_SERVERS>
   REDPANDA_SASL_USERNAME=<YOUR_USERNAME>
   REDPANDA_SASL_PASSWORD=<YOUR_PASSWORD>
   REDPANDA_SASL_MECHANISM=SCRAM-SHA-256
   REDPANDA_SECURITY_PROTOCOL=SASL_SSL
   ```

## Step 4: Test Connection (T012)

Use the provided test script to verify connectivity:

```bash
cd phase-5-cloud-deployment/scripts
python test-redpanda-connection.py
```

Expected output:
```
✓ Connected to Redpanda Cloud
✓ Topics verified: task-events, reminders, task-updates
✓ Producer test: SUCCESS
✓ Consumer test: SUCCESS
```

## Troubleshooting

**Connection Timeout**:
- Verify bootstrap servers URL
- Check firewall rules
- Ensure SASL credentials are correct

**Authentication Failed**:
- Verify SASL mechanism (SCRAM-SHA-256)
- Check username/password
- Ensure user has topic permissions

**Topic Not Found**:
- Verify topics were created
- Check topic names match exactly
- Ensure user has read permissions

## Next Steps

After successful setup:
1. Proceed to Dapr integration (T013-T018)
2. Configure Dapr Kafka pub/sub component
3. Test event publishing and consumption
