#!/bin/bash

# Phase IV - Minikube Setup Script (Linux/macOS)
# Initializes Minikube cluster with appropriate configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "Phase IV - Minikube Setup"
echo "========================================="
echo ""

# Configuration
CPUS=${MINIKUBE_CPUS:-4}
MEMORY=${MINIKUBE_MEMORY:-8192}
DISK_SIZE=${MINIKUBE_DISK_SIZE:-20g}
DRIVER=${MINIKUBE_DRIVER:-docker}

echo -e "${BLUE}Configuration:${NC}"
echo "  CPUs: $CPUS"
echo "  Memory: ${MEMORY}MB"
echo "  Disk Size: $DISK_SIZE"
echo "  Driver: $DRIVER"
echo ""

# Check if Minikube is already running
if minikube status &> /dev/null; then
    echo -e "${YELLOW}⚠ Minikube is already running${NC}"
    echo ""
    read -p "Do you want to delete and recreate the cluster? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Deleting existing cluster..."
        minikube delete
    else
        echo "Using existing cluster"
        echo ""
        echo -e "${GREEN}✓ Minikube cluster ready${NC}"
        exit 0
    fi
fi

# Start Minikube
echo "Starting Minikube cluster..."
echo ""

minikube start \
    --cpus=$CPUS \
    --memory=$MEMORY \
    --disk-size=$DISK_SIZE \
    --driver=$DRIVER

echo ""
echo -e "${GREEN}✓ Minikube cluster started${NC}"
echo ""

# Enable required addons
echo "Enabling required addons..."
echo ""

echo "  - Enabling Ingress controller..."
minikube addons enable ingress

echo "  - Enabling Metrics server..."
minikube addons enable metrics-server

echo ""
echo -e "${GREEN}✓ Addons enabled${NC}"
echo ""

# Verify cluster
echo "Verifying cluster..."
echo ""

kubectl cluster-info
echo ""

kubectl get nodes
echo ""

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)
echo -e "${BLUE}Minikube IP:${NC} $MINIKUBE_IP"
echo ""

# Instructions for hosts file
echo "========================================="
echo "Next Steps"
echo "========================================="
echo ""
echo "1. Add the following to your hosts file:"
echo ""
echo -e "   ${YELLOW}$MINIKUBE_IP todo.local${NC}"
echo ""
echo "   On Linux/macOS:"
echo "   sudo nano /etc/hosts"
echo ""
echo "2. Build Docker images:"
echo "   ./scripts/build-images.sh"
echo ""
echo "3. Deploy the application:"
echo "   ./scripts/deploy.sh"
echo ""
echo -e "${GREEN}✓ Minikube setup complete!${NC}"
