#!/bin/bash

# Phase IV - Helm Deployment Script (Linux/macOS)
# Deploys the Todo App using Helm chart with configuration profile support

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
    echo "  -f, --values-file FILE    Path to custom values file"
    echo "  -p, --profile PROFILE     Use predefined profile (dev, test, prod)"
    echo "  -n, --namespace NAME      Kubernetes namespace (default: todo-app)"
    echo "  -r, --release NAME        Helm release name (default: todo-app)"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Deploy with default values"
    echo "  $0 -p dev                             # Deploy with development profile"
    echo "  $0 -p test                            # Deploy with testing profile"
    echo "  $0 -f custom-values.yaml              # Deploy with custom values file"
    echo "  $0 -p dev -n todo-dev                 # Deploy dev profile to custom namespace"
    echo ""
    echo "Available profiles:"
    echo "  dev   - Development profile (minimal resources, single replica)"
    echo "  test  - Testing profile (production-like, multiple replicas)"
    echo ""
    exit 1
}

# Parse command-line arguments
VALUES_FILE=""
PROFILE=""
RELEASE_NAME=${RELEASE_NAME:-todo-app}
NAMESPACE=${NAMESPACE:-todo-app}
CHART_PATH="helm/todo-app"

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--values-file)
            VALUES_FILE="$2"
            shift 2
            ;;
        -p|--profile)
            PROFILE="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -r|--release)
            RELEASE_NAME="$2"
            shift 2
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

# Resolve profile to values file
if [ -n "$PROFILE" ]; then
    case $PROFILE in
        dev)
            VALUES_FILE="$CHART_PATH/values-dev.yaml"
            ;;
        test)
            VALUES_FILE="$CHART_PATH/values-test.yaml"
            ;;
        prod)
            echo -e "${RED}Error: Production profile not yet implemented${NC}"
            echo "Use a custom values file with -f option"
            exit 1
            ;;
        *)
            echo -e "${RED}Error: Unknown profile: $PROFILE${NC}"
            echo "Available profiles: dev, test"
            exit 1
            ;;
    esac
fi

# Validate values file if specified
if [ -n "$VALUES_FILE" ]; then
    if [ ! -f "$VALUES_FILE" ]; then
        echo -e "${RED}Error: Values file not found: $VALUES_FILE${NC}"
        exit 1
    fi
fi

echo "========================================="
echo "Phase IV - Helm Deployment"
echo "========================================="
echo ""
echo -e "${BLUE}Release Name:${NC} $RELEASE_NAME"
echo -e "${BLUE}Namespace:${NC} $NAMESPACE"
if [ -n "$VALUES_FILE" ]; then
    echo -e "${BLUE}Values File:${NC} $VALUES_FILE"
    if [ -n "$PROFILE" ]; then
        echo -e "${BLUE}Profile:${NC} $PROFILE"
    fi
else
    echo -e "${BLUE}Values File:${NC} default (values.yaml)"
fi
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

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}✗ Helm is not installed${NC}"
    echo "Please install Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi

echo -e "${GREEN}✓ Helm is installed${NC}"
echo ""

# Lint the chart
echo "Linting Helm chart..."
if helm lint "$CHART_PATH"; then
    echo -e "${GREEN}✓ Chart lint passed${NC}"
else
    echo -e "${RED}✗ Chart lint failed${NC}"
    exit 1
fi
echo ""

# Check if release already exists
if helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
    echo -e "${YELLOW}⚠ Release '$RELEASE_NAME' already exists${NC}"
    echo ""
    read -p "Do you want to upgrade the existing release? (y/N): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Upgrading release..."

        if [ -n "$VALUES_FILE" ]; then
            helm upgrade "$RELEASE_NAME" "$CHART_PATH" \
                --namespace "$NAMESPACE" \
                --values "$VALUES_FILE" \
                --wait \
                --timeout 5m
        else
            helm upgrade "$RELEASE_NAME" "$CHART_PATH" \
                --namespace "$NAMESPACE" \
                --wait \
                --timeout 5m
        fi

        echo ""
        echo -e "${GREEN}✓ Release upgraded successfully${NC}"
    else
        echo "Upgrade cancelled"
        exit 0
    fi
else
    echo "Installing release..."

    if [ -n "$VALUES_FILE" ]; then
        helm install "$RELEASE_NAME" "$CHART_PATH" \
            --namespace "$NAMESPACE" \
            --create-namespace \
            --values "$VALUES_FILE" \
            --wait \
            --timeout 5m
    else
        helm install "$RELEASE_NAME" "$CHART_PATH" \
            --namespace "$NAMESPACE" \
            --create-namespace \
            --wait \
            --timeout 5m
    fi

    echo ""
    echo -e "${GREEN}✓ Release installed successfully${NC}"
fi

echo ""

# Get deployment status
echo "========================================="
echo "Deployment Status"
echo "========================================="
echo ""

helm status "$RELEASE_NAME" -n "$NAMESPACE"

echo ""
echo "========================================="
echo "Resources"
echo "========================================="
echo ""

kubectl get all -n "$NAMESPACE"

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
echo "  - View release: helm list -n $NAMESPACE"
echo "  - View values: helm get values $RELEASE_NAME -n $NAMESPACE"
echo "  - Upgrade: helm upgrade $RELEASE_NAME $CHART_PATH -n $NAMESPACE"
echo "  - Uninstall: helm uninstall $RELEASE_NAME -n $NAMESPACE"
