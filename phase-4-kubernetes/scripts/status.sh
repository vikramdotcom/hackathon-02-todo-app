#!/bin/bash

# Phase IV - Status Check Script (Linux/macOS)
# Displays the current status of the Todo App deployment

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "Phase IV - Todo App Status"
echo "========================================="
echo ""

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo -e "${RED}✗ Minikube is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Minikube is running${NC}"
echo ""

# Check if namespace exists
if ! kubectl get namespace todo-app &> /dev/null; then
    echo -e "${RED}✗ Todo App namespace not found${NC}"
    echo "Run ./scripts/deploy.sh to deploy the application"
    exit 1
fi

echo -e "${GREEN}✓ Todo App namespace exists${NC}"
echo ""

# Display pods
echo "========================================="
echo "Pods"
echo "========================================="
kubectl get pods -n todo-app -o wide

echo ""

# Display services
echo "========================================="
echo "Services"
echo "========================================="
kubectl get services -n todo-app

echo ""

# Display deployments
echo "========================================="
echo "Deployments"
echo "========================================="
kubectl get deployments -n todo-app

echo ""

# Display ingress
echo "========================================="
echo "Ingress"
echo "========================================="
kubectl get ingress -n todo-app

echo ""

# Display PVC
echo "========================================="
echo "Persistent Volume Claims"
echo "========================================="
kubectl get pvc -n todo-app

echo ""

# Check pod health
echo "========================================="
echo "Pod Health Status"
echo "========================================="

TOTAL_PODS=$(kubectl get pods -n todo-app --no-headers 2>/dev/null | wc -l)
READY_PODS=$(kubectl get pods -n todo-app --no-headers 2>/dev/null | grep "Running" | grep -E "([0-9]+)/\1" | wc -l)

echo -e "Total Pods: ${BLUE}$TOTAL_PODS${NC}"
echo -e "Ready Pods: ${GREEN}$READY_PODS${NC}"

if [ "$READY_PODS" -eq "$TOTAL_PODS" ] && [ "$TOTAL_PODS" -gt 0 ]; then
    echo -e "${GREEN}✓ All pods are healthy${NC}"
else
    echo -e "${YELLOW}⚠ Some pods are not ready${NC}"
fi

echo ""

# Display access information
echo "========================================="
echo "Access Information"
echo "========================================="

MINIKUBE_IP=$(minikube ip)
echo -e "${BLUE}Application URL:${NC} http://todo.local"
echo -e "${BLUE}Minikube IP:${NC} $MINIKUBE_IP"
echo ""
echo "Add to hosts file:"
echo -e "${YELLOW}$MINIKUBE_IP todo.local${NC}"

echo ""

# Display resource usage
echo "========================================="
echo "Resource Usage"
echo "========================================="
kubectl top pods -n todo-app 2>/dev/null || echo "Metrics not available (metrics-server may not be ready)"

echo ""
echo "Useful commands:"
echo "  - View logs: kubectl logs -f deployment/backend -n todo-app"
echo "  - Describe pod: kubectl describe pod <pod-name> -n todo-app"
echo "  - Scale deployment: kubectl scale deployment/backend --replicas=3 -n todo-app"
echo "  - Port forward: kubectl port-forward service/frontend 3000:3000 -n todo-app"
