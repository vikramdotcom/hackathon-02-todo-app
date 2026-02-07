#!/bin/bash

# Phase IV - Cleanup Script (Linux/macOS)
# Removes all Kubernetes resources and optionally Minikube cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --all                 Remove everything (Helm release, namespace, Minikube)"
    echo "  --helm                Remove Helm release only"
    echo "  --namespace           Remove namespace (includes all resources)"
    echo "  --minikube            Stop and delete Minikube cluster"
    echo "  --images              Remove Docker images"
    echo "  --keep-minikube       Remove resources but keep Minikube running"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --all                      # Remove everything"
    echo "  $0 --helm                     # Remove Helm release only"
    echo "  $0 --namespace                # Remove namespace and all resources"
    echo "  $0 --keep-minikube            # Remove resources but keep Minikube"
    echo "  $0 --helm --images            # Remove Helm release and images"
    echo ""
    exit 1
}

# Configuration
RELEASE_NAME=${RELEASE_NAME:-todo-app}
NAMESPACE=${NAMESPACE:-todo-app}
REMOVE_HELM=false
REMOVE_NAMESPACE=false
REMOVE_MINIKUBE=false
REMOVE_IMAGES=false
REMOVE_ALL=false

# Parse command-line arguments
if [ $# -eq 0 ]; then
    usage
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            REMOVE_ALL=true
            REMOVE_HELM=true
            REMOVE_NAMESPACE=true
            REMOVE_MINIKUBE=true
            REMOVE_IMAGES=true
            shift
            ;;
        --helm)
            REMOVE_HELM=true
            shift
            ;;
        --namespace)
            REMOVE_NAMESPACE=true
            shift
            ;;
        --minikube)
            REMOVE_MINIKUBE=true
            shift
            ;;
        --images)
            REMOVE_IMAGES=true
            shift
            ;;
        --keep-minikube)
            REMOVE_HELM=true
            REMOVE_NAMESPACE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}"
            usage
            ;;
    esac
done

echo "========================================="
echo "Phase IV - Cleanup"
echo "========================================="
echo ""

# Confirmation prompt
echo -e "${YELLOW}⚠️  WARNING: This will remove the following:${NC}"
echo ""
if [ "$REMOVE_HELM" = true ]; then
    echo "  - Helm release: $RELEASE_NAME"
fi
if [ "$REMOVE_NAMESPACE" = true ]; then
    echo "  - Namespace: $NAMESPACE (all resources)"
fi
if [ "$REMOVE_MINIKUBE" = true ]; then
    echo "  - Minikube cluster (complete deletion)"
fi
if [ "$REMOVE_IMAGES" = true ]; then
    echo "  - Docker images (todo-frontend, todo-backend)"
fi
echo ""
echo -n "Are you sure you want to continue? (y/N): "
read -r response

if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""

# Remove Helm release
if [ "$REMOVE_HELM" = true ]; then
    echo "========================================="
    echo "Removing Helm Release"
    echo "========================================="
    echo ""

    if helm list -n "$NAMESPACE" 2>/dev/null | grep -q "$RELEASE_NAME"; then
        echo "Uninstalling Helm release: $RELEASE_NAME"
        helm uninstall "$RELEASE_NAME" -n "$NAMESPACE"

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Helm release removed${NC}"
        else
            echo -e "${RED}✗ Failed to remove Helm release${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Helm release not found: $RELEASE_NAME${NC}"
    fi

    echo ""
fi

# Remove namespace
if [ "$REMOVE_NAMESPACE" = true ]; then
    echo "========================================="
    echo "Removing Namespace"
    echo "========================================="
    echo ""

    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        echo "Deleting namespace: $NAMESPACE"
        kubectl delete namespace "$NAMESPACE"

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Namespace removed${NC}"
        else
            echo -e "${RED}✗ Failed to remove namespace${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Namespace not found: $NAMESPACE${NC}"
    fi

    echo ""
fi

# Remove Docker images
if [ "$REMOVE_IMAGES" = true ]; then
    echo "========================================="
    echo "Removing Docker Images"
    echo "========================================="
    echo ""

    # Remove frontend images
    if docker images | grep -q "todo-frontend"; then
        echo "Removing frontend images..."
        docker rmi $(docker images -q todo-frontend) -f 2>/dev/null || true
        echo -e "${GREEN}✓ Frontend images removed${NC}"
    else
        echo -e "${YELLOW}⚠ No frontend images found${NC}"
    fi

    # Remove backend images
    if docker images | grep -q "todo-backend"; then
        echo "Removing backend images..."
        docker rmi $(docker images -q todo-backend) -f 2>/dev/null || true
        echo -e "${GREEN}✓ Backend images removed${NC}"
    else
        echo -e "${YELLOW}⚠ No backend images found${NC}"
    fi

    echo ""
fi

# Stop and delete Minikube
if [ "$REMOVE_MINIKUBE" = true ]; then
    echo "========================================="
    echo "Removing Minikube Cluster"
    echo "========================================="
    echo ""

    if minikube status &> /dev/null; then
        echo "Stopping Minikube..."
        minikube stop

        echo "Deleting Minikube cluster..."
        minikube delete

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Minikube cluster removed${NC}"
        else
            echo -e "${RED}✗ Failed to remove Minikube cluster${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Minikube not running${NC}"
    fi

    echo ""
fi

# Summary
echo "========================================="
echo "Cleanup Summary"
echo "========================================="
echo ""

if [ "$REMOVE_ALL" = true ]; then
    echo -e "${GREEN}✓ Complete cleanup finished${NC}"
    echo ""
    echo "All resources have been removed:"
    echo "  - Helm release"
    echo "  - Namespace and all resources"
    echo "  - Docker images"
    echo "  - Minikube cluster"
else
    echo -e "${GREEN}✓ Cleanup finished${NC}"
    echo ""
    echo "Removed:"
    if [ "$REMOVE_HELM" = true ]; then
        echo "  - Helm release"
    fi
    if [ "$REMOVE_NAMESPACE" = true ]; then
        echo "  - Namespace and all resources"
    fi
    if [ "$REMOVE_IMAGES" = true ]; then
        echo "  - Docker images"
    fi
    if [ "$REMOVE_MINIKUBE" = true ]; then
        echo "  - Minikube cluster"
    fi
fi

echo ""

# Next steps
if [ "$REMOVE_MINIKUBE" = false ]; then
    echo "Next steps:"
    echo "  - To redeploy: ./scripts/deploy.sh"
    echo "  - To remove Minikube: $0 --minikube"
else
    echo "Next steps:"
    echo "  - To start fresh: ./scripts/setup-minikube.sh"
    echo "  - Then deploy: ./scripts/deploy.sh"
fi

echo ""
echo -e "${GREEN}✓ Cleanup complete!${NC}"
