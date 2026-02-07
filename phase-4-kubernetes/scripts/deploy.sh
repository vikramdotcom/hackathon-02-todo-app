#!/bin/bash

# Phase IV - Deployment Script (Linux/macOS)
# Deploys the Todo App to Kubernetes cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "Phase IV - Deploying Todo App"
echo "========================================="
echo ""

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo -e "${RED}✗ Minikube is not running${NC}"
    echo "Please start Minikube first: ./scripts/setup-minikube.sh"
    exit 1
fi

echo -e "${GREEN}✓ Minikube is running${NC}"
echo ""

# Check if images exist
echo "Checking Docker images..."
if ! docker images | grep -q "todo-frontend"; then
    echo -e "${RED}✗ Frontend image not found${NC}"
    echo "Please build images first: ./scripts/build-images.sh"
    exit 1
fi

if ! docker images | grep -q "todo-backend"; then
    echo -e "${RED}✗ Backend image not found${NC}"
    echo "Please build images first: ./scripts/build-images.sh"
    exit 1
fi

echo -e "${GREEN}✓ Docker images found${NC}"
echo ""

# Create namespace
echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml
echo -e "${GREEN}✓ Namespace created${NC}"
echo ""

# Check if secrets exist
echo "Checking secrets..."
if ! kubectl get secret todo-app-secrets -n todo-app &> /dev/null; then
    echo -e "${YELLOW}⚠ Secrets not found${NC}"
    echo ""
    echo "Creating secrets from example file..."

    if [ ! -f k8s/secret.yaml ]; then
        echo "Copying secret.yaml.example to secret.yaml..."
        cp k8s/secret.yaml.example k8s/secret.yaml
        echo ""
        echo -e "${YELLOW}⚠ Using default secrets${NC}"
        echo "Please update k8s/secret.yaml with your actual secrets before production use"
        echo ""
    fi

    kubectl apply -f k8s/secret.yaml
    echo -e "${GREEN}✓ Secrets created${NC}"
else
    echo -e "${GREEN}✓ Secrets already exist${NC}"
fi
echo ""

# Apply ConfigMap
echo "Applying ConfigMap..."
kubectl apply -f k8s/configmap.yaml
echo -e "${GREEN}✓ ConfigMap applied${NC}"
echo ""

# Apply PersistentVolumeClaim
echo "Creating PersistentVolumeClaim..."
kubectl apply -f k8s/postgres-pvc.yaml
echo -e "${GREEN}✓ PVC created${NC}"
echo ""

# Deploy database
echo "Deploying database..."
kubectl apply -f k8s/database-deployment.yaml
kubectl apply -f k8s/database-service.yaml
echo -e "${GREEN}✓ Database deployed${NC}"
echo ""

# Wait for database to be ready
echo "Waiting for database to be ready..."
kubectl wait --for=condition=ready pod -l component=database -n todo-app --timeout=120s
echo -e "${GREEN}✓ Database is ready${NC}"
echo ""

# Deploy backend
echo "Deploying backend..."
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
echo -e "${GREEN}✓ Backend deployed${NC}"
echo ""

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
kubectl wait --for=condition=ready pod -l component=backend -n todo-app --timeout=120s
echo -e "${GREEN}✓ Backend is ready${NC}"
echo ""

# Deploy frontend
echo "Deploying frontend..."
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
echo -e "${GREEN}✓ Frontend deployed${NC}"
echo ""

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
kubectl wait --for=condition=ready pod -l component=frontend -n todo-app --timeout=120s
echo -e "${GREEN}✓ Frontend is ready${NC}"
echo ""

# Apply Ingress
echo "Applying Ingress..."
kubectl apply -f k8s/ingress.yaml
echo -e "${GREEN}✓ Ingress applied${NC}"
echo ""

# Get deployment status
echo "========================================="
echo "Deployment Status"
echo "========================================="
echo ""

kubectl get all -n todo-app

echo ""
echo "========================================="
echo "Access Information"
echo "========================================="
echo ""

MINIKUBE_IP=$(minikube ip)
echo -e "${BLUE}Application URL:${NC} http://todo.local"
echo -e "${BLUE}Minikube IP:${NC} $MINIKUBE_IP"
echo ""
echo "Make sure you have added the following to your hosts file:"
echo -e "${YELLOW}$MINIKUBE_IP todo.local${NC}"
echo ""
echo "On Linux/macOS:"
echo "  sudo nano /etc/hosts"
echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo ""
echo "Useful commands:"
echo "  - View logs: kubectl logs -f deployment/backend -n todo-app"
echo "  - Check status: kubectl get pods -n todo-app"
echo "  - Scale replicas: kubectl scale deployment/backend --replicas=3 -n todo-app"
