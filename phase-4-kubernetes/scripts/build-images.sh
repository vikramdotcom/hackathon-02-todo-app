#!/bin/bash

# Phase IV - Docker Image Build Script (Linux/macOS)
# Builds Docker images for frontend and backend using Minikube's Docker daemon

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "Phase IV - Building Docker Images"
echo "========================================="
echo ""

# Version tagging
# Usage: ./build-images.sh [version]
# If no version provided, uses git commit SHA or timestamp
VERSION=${1:-}

if [ -z "$VERSION" ]; then
    # Try to get git commit SHA
    if git rev-parse --git-dir > /dev/null 2>&1; then
        VERSION=$(git rev-parse --short HEAD)
        echo -e "${BLUE}Using git commit SHA as version: $VERSION${NC}"
    else
        # Fallback to timestamp
        VERSION=$(date +%Y%m%d-%H%M%S)
        echo -e "${BLUE}Using timestamp as version: $VERSION${NC}"
    fi
else
    echo -e "${BLUE}Using provided version: $VERSION${NC}"
fi

# Always tag as latest as well
TAG_LATEST=true

echo ""

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo -e "${RED}✗ Minikube is not running${NC}"
    echo "Please start Minikube first: ./scripts/setup-minikube.sh"
    exit 1
fi

echo -e "${GREEN}✓ Minikube is running${NC}"
echo ""

# Configure Docker to use Minikube's daemon
echo "Configuring Docker to use Minikube's daemon..."
eval $(minikube docker-env)
echo -e "${GREEN}✓ Docker configured${NC}"
echo ""

# Build frontend image
echo "========================================="
echo "Building Frontend Image"
echo "========================================="
echo ""

cd ../phase-3-ai-chatbot/frontend

echo "Building todo-frontend:$VERSION..."
docker build \
    -f ../../phase-4-kubernetes/docker/frontend/Dockerfile \
    -t todo-frontend:$VERSION \
    .

if [ "$TAG_LATEST" = true ]; then
    echo "Tagging as latest..."
    docker tag todo-frontend:$VERSION todo-frontend:latest
fi

echo ""
echo -e "${GREEN}✓ Frontend image built successfully${NC}"
echo "  - todo-frontend:$VERSION"
if [ "$TAG_LATEST" = true ]; then
    echo "  - todo-frontend:latest"
fi
echo ""

# Build backend image
echo "========================================="
echo "Building Backend Image"
echo "========================================="
echo ""

cd ../backend

echo "Building todo-backend:$VERSION..."
docker build \
    -f ../../phase-4-kubernetes/docker/backend/Dockerfile \
    -t todo-backend:$VERSION \
    .

if [ "$TAG_LATEST" = true ]; then
    echo "Tagging as latest..."
    docker tag todo-backend:$VERSION todo-backend:latest
fi

echo ""
echo -e "${GREEN}✓ Backend image built successfully${NC}"
echo "  - todo-backend:$VERSION"
if [ "$TAG_LATEST" = true ]; then
    echo "  - todo-backend:latest"
fi
echo ""

# Return to phase-4-kubernetes directory
cd ../../phase-4-kubernetes

# Verify images
echo "========================================="
echo "Verifying Images"
echo "========================================="
echo ""

docker images | grep -E "todo-(frontend|backend)"

echo ""
echo -e "${GREEN}✓ All images built successfully!${NC}"
echo ""
echo "Image versions:"
echo "  Frontend: todo-frontend:$VERSION"
echo "  Backend: todo-backend:$VERSION"
echo ""
echo "Next steps:"
echo "  1. Create secrets: kubectl apply -f k8s/secret.yaml"
echo "  2. Deploy application: ./scripts/deploy.sh"
echo ""
echo "To deploy with specific version:"
echo "  helm install todo-app ./helm/todo-app -n todo-app \\"
echo "    --set frontend.image.tag=$VERSION \\"
echo "    --set backend.image.tag=$VERSION"
