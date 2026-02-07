#!/bin/bash

# Phase IV - Service Scaling Script (Linux/macOS)
# Helper script for scaling services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
NAMESPACE="todo-app"
SERVICE=""
REPLICAS=""

# Usage function
usage() {
    echo "Usage: $0 <service> <replicas>"
    echo ""
    echo "Services:"
    echo "  frontend   - Scale frontend deployment"
    echo "  backend    - Scale backend deployment"
    echo "  all        - Scale both frontend and backend"
    echo ""
    echo "Examples:"
    echo "  $0 frontend 3      # Scale frontend to 3 replicas"
    echo "  $0 backend 5       # Scale backend to 5 replicas"
    echo "  $0 all 3           # Scale both to 3 replicas"
    echo ""
    exit 1
}

# Check arguments
if [ $# -lt 2 ]; then
    usage
fi

SERVICE=$1
REPLICAS=$2

# Validate replicas is a number
if ! [[ "$REPLICAS" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}Error: Replicas must be a positive number${NC}"
    exit 1
fi

# Check if namespace exists
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${RED}Error: Namespace '$NAMESPACE' not found${NC}"
    echo "Please deploy the application first"
    exit 1
fi

echo "========================================="
echo "Service Scaling"
echo "========================================="
echo ""

# Scale function
scale_service() {
    local service=$1
    local replicas=$2
    local deployment_name=""

    case $service in
        frontend)
            deployment_name="frontend"
            ;;
        backend)
            deployment_name="backend"
            ;;
        *)
            echo -e "${RED}Error: Unknown service '$service'${NC}"
            return 1
            ;;
    esac

    echo -n "Scaling $service to $replicas replicas... "

    if kubectl scale deployment/$deployment_name --replicas=$replicas -n $NAMESPACE &> /dev/null; then
        echo -e "${GREEN}✓${NC}"

        # Wait for rollout
        echo -n "Waiting for rollout to complete... "
        if kubectl rollout status deployment/$deployment_name -n $NAMESPACE --timeout=120s &> /dev/null; then
            echo -e "${GREEN}✓${NC}"

            # Get current status
            READY=$(kubectl get deployment $deployment_name -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
            DESIRED=$(kubectl get deployment $deployment_name -n $NAMESPACE -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

            echo -e "${BLUE}Status:${NC} $READY/$DESIRED ready"
        else
            echo -e "${YELLOW}⚠${NC}"
            echo "Rollout is taking longer than expected"
        fi
    else
        echo -e "${RED}✗${NC}"
        echo "Failed to scale $service"
        return 1
    fi

    echo ""
}

# Scale services
case $SERVICE in
    frontend|backend)
        scale_service $SERVICE $REPLICAS
        ;;
    all)
        scale_service "frontend" $REPLICAS
        scale_service "backend" $REPLICAS
        ;;
    *)
        echo -e "${RED}Error: Unknown service '$SERVICE'${NC}"
        usage
        ;;
esac

# Show current status
echo "========================================="
echo "Current Deployment Status"
echo "========================================="
echo ""

kubectl get deployments -n $NAMESPACE

echo ""
echo "========================================="
echo "Pod Status"
echo "========================================="
echo ""

kubectl get pods -n $NAMESPACE -o wide

echo ""
echo -e "${GREEN}✓ Scaling complete!${NC}"
echo ""
echo "Monitor resource usage:"
echo "  kubectl top pods -n $NAMESPACE"
echo "  kubectl top nodes"
