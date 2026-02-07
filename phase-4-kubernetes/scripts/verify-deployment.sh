#!/bin/bash

# Phase IV - Deployment Verification Script (Linux/macOS)
# Verifies deployment consistency and reproducibility

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
WARNINGS=0

echo "========================================="
echo "Phase IV - Deployment Verification"
echo "========================================="
echo ""

# Function to check and report
check() {
    local name=$1
    local command=$2

    echo -n "Checking $name... "

    if eval "$command" &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
        return 1
    fi
}

# Function for warnings
warn() {
    local name=$1
    local command=$2

    echo -n "Checking $name... "

    if eval "$command" &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠${NC}"
        ((WARNINGS++))
        return 1
    fi
}

# 1. Environment Verification
echo "========================================="
echo "1. Environment Verification"
echo "========================================="
echo ""

# Detect OS
OS_TYPE=$(uname -s)
echo -e "${BLUE}Operating System:${NC} $OS_TYPE"

# Check prerequisites
check "Docker installed" "command -v docker"
check "Minikube installed" "command -v minikube"
check "kubectl installed" "command -v kubectl"
check "Helm installed" "command -v helm"

echo ""

# 2. Cluster Verification
echo "========================================="
echo "2. Cluster Verification"
echo "========================================="
echo ""

check "Minikube running" "minikube status"
check "kubectl configured" "kubectl cluster-info"

# Get cluster info
MINIKUBE_VERSION=$(minikube version --short 2>/dev/null || echo "unknown")
KUBECTL_VERSION=$(kubectl version --client --short 2>/dev/null | head -1 || echo "unknown")
HELM_VERSION=$(helm version --short 2>/dev/null || echo "unknown")

echo ""
echo -e "${BLUE}Cluster Information:${NC}"
echo "  Minikube: $MINIKUBE_VERSION"
echo "  kubectl: $KUBECTL_VERSION"
echo "  Helm: $HELM_VERSION"
echo ""

# 3. Image Verification
echo "========================================="
echo "3. Image Verification"
echo "========================================="
echo ""

# Configure Docker to use Minikube's daemon
eval $(minikube docker-env)

# Check for images
if docker images | grep -q "todo-frontend"; then
    FRONTEND_IMAGES=$(docker images todo-frontend --format "{{.Tag}}" | tr '\n' ', ' | sed 's/,$//')
    echo -e "${GREEN}✓${NC} Frontend images found: $FRONTEND_IMAGES"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Frontend images not found"
    ((FAILED++))
fi

if docker images | grep -q "todo-backend"; then
    BACKEND_IMAGES=$(docker images todo-backend --format "{{.Tag}}" | tr '\n' ', ' | sed 's/,$//')
    echo -e "${GREEN}✓${NC} Backend images found: $BACKEND_IMAGES"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Backend images not found"
    ((FAILED++))
fi

echo ""

# 4. Deployment Verification
echo "========================================="
echo "4. Deployment Verification"
echo "========================================="
echo ""

if kubectl get namespace todo-app &> /dev/null; then
    echo -e "${GREEN}✓${NC} Namespace exists"
    ((PASSED++))

    # Check deployments
    FRONTEND_REPLICAS=$(kubectl get deployment frontend -n todo-app -o jsonpath='{.status.replicas}' 2>/dev/null || echo "0")
    FRONTEND_READY=$(kubectl get deployment frontend -n todo-app -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
    BACKEND_REPLICAS=$(kubectl get deployment backend -n todo-app -o jsonpath='{.status.replicas}' 2>/dev/null || echo "0")
    BACKEND_READY=$(kubectl get deployment backend -n todo-app -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
    DATABASE_REPLICAS=$(kubectl get deployment database -n todo-app -o jsonpath='{.status.replicas}' 2>/dev/null || echo "0")
    DATABASE_READY=$(kubectl get deployment database -n todo-app -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")

    echo ""
    echo -e "${BLUE}Deployment Status:${NC}"
    echo "  Frontend: $FRONTEND_READY/$FRONTEND_REPLICAS ready"
    echo "  Backend: $BACKEND_READY/$BACKEND_REPLICAS ready"
    echo "  Database: $DATABASE_READY/$DATABASE_REPLICAS ready"
    echo ""

    if [ "$FRONTEND_READY" = "$FRONTEND_REPLICAS" ] && [ "$FRONTEND_REPLICAS" != "0" ]; then
        echo -e "${GREEN}✓${NC} Frontend deployment healthy"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Frontend deployment not healthy"
        ((FAILED++))
    fi

    if [ "$BACKEND_READY" = "$BACKEND_REPLICAS" ] && [ "$BACKEND_REPLICAS" != "0" ]; then
        echo -e "${GREEN}✓${NC} Backend deployment healthy"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Backend deployment not healthy"
        ((FAILED++))
    fi

    if [ "$DATABASE_READY" = "$DATABASE_REPLICAS" ] && [ "$DATABASE_REPLICAS" != "0" ]; then
        echo -e "${GREEN}✓${NC} Database deployment healthy"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Database deployment not healthy"
        ((FAILED++))
    fi
else
    echo -e "${YELLOW}⚠${NC} Namespace not found (deployment not yet done)"
    ((WARNINGS++))
fi

echo ""

# 5. Configuration Verification
echo "========================================="
echo "5. Configuration Verification"
echo "========================================="
echo ""

if kubectl get namespace todo-app &> /dev/null; then
    check "ConfigMap exists" "kubectl get configmap todo-app-config -n todo-app"
    check "Secret exists" "kubectl get secret todo-app-secrets -n todo-app"
    check "PVC exists" "kubectl get pvc postgres-pvc -n todo-app"

    # Verify ConfigMap values
    echo ""
    echo -e "${BLUE}ConfigMap Values:${NC}"
    kubectl get configmap todo-app-config -n todo-app -o jsonpath='{.data}' | jq '.' 2>/dev/null || echo "  (jq not available)"
fi

echo ""

# 6. Version Consistency
echo "========================================="
echo "6. Version Consistency"
echo "========================================="
echo ""

if kubectl get namespace todo-app &> /dev/null; then
    # Get image versions from deployments
    FRONTEND_IMAGE=$(kubectl get deployment frontend -n todo-app -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || echo "not found")
    BACKEND_IMAGE=$(kubectl get deployment backend -n todo-app -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || echo "not found")

    echo -e "${BLUE}Deployed Images:${NC}"
    echo "  Frontend: $FRONTEND_IMAGE"
    echo "  Backend: $BACKEND_IMAGE"
    echo ""

    # Check if versions match
    FRONTEND_TAG=$(echo $FRONTEND_IMAGE | cut -d':' -f2)
    BACKEND_TAG=$(echo $BACKEND_IMAGE | cut -d':' -f2)

    if [ "$FRONTEND_TAG" = "$BACKEND_TAG" ]; then
        echo -e "${GREEN}✓${NC} Image versions consistent"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} Image versions differ (Frontend: $FRONTEND_TAG, Backend: $BACKEND_TAG)"
        ((WARNINGS++))
    fi
fi

echo ""

# 7. Helm Release Verification (if using Helm)
echo "========================================="
echo "7. Helm Release Verification"
echo "========================================="
echo ""

if helm list -n todo-app 2>/dev/null | grep -q "todo-app"; then
    echo -e "${GREEN}✓${NC} Helm release found"
    ((PASSED++))

    HELM_STATUS=$(helm status todo-app -n todo-app -o json 2>/dev/null)
    HELM_REVISION=$(echo $HELM_STATUS | jq -r '.version' 2>/dev/null || echo "unknown")
    HELM_CHART=$(echo $HELM_STATUS | jq -r '.chart' 2>/dev/null || echo "unknown")

    echo ""
    echo -e "${BLUE}Helm Release:${NC}"
    echo "  Chart: $HELM_CHART"
    echo "  Revision: $HELM_REVISION"
else
    echo -e "${YELLOW}⚠${NC} No Helm release found (using direct kubectl deployment)"
    ((WARNINGS++))
fi

echo ""

# 8. Reproducibility Check
echo "========================================="
echo "8. Reproducibility Check"
echo "========================================="
echo ""

# Check if deployment is deterministic
echo "Checking deployment reproducibility..."

# Verify all resources have proper labels
LABELED_RESOURCES=$(kubectl get all -n todo-app -o json 2>/dev/null | jq '[.items[] | select(.metadata.labels != null)] | length' 2>/dev/null || echo "0")
TOTAL_RESOURCES=$(kubectl get all -n todo-app -o json 2>/dev/null | jq '.items | length' 2>/dev/null || echo "0")

if [ "$LABELED_RESOURCES" = "$TOTAL_RESOURCES" ] && [ "$TOTAL_RESOURCES" != "0" ]; then
    echo -e "${GREEN}✓${NC} All resources properly labeled"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Some resources missing labels ($LABELED_RESOURCES/$TOTAL_RESOURCES)"
    ((WARNINGS++))
fi

# Check for consistent naming
echo -n "Checking naming consistency... "
INCONSISTENT_NAMES=$(kubectl get all -n todo-app -o name 2>/dev/null | grep -v "todo-app\|frontend\|backend\|database" | wc -l)
if [ "$INCONSISTENT_NAMES" = "0" ]; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} ($INCONSISTENT_NAMES resources with non-standard names)"
    ((WARNINGS++))
fi

echo ""

# Summary
echo "========================================="
echo "Verification Summary"
echo "========================================="
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

# Calculate success rate
TOTAL=$((PASSED + FAILED + WARNINGS))
if [ $TOTAL -gt 0 ]; then
    SUCCESS_RATE=$((PASSED * 100 / TOTAL))
    echo "Success Rate: ${SUCCESS_RATE}%"
    echo ""
fi

# Final verdict
if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✓ Deployment is fully verified and reproducible!${NC}"
        echo ""
        echo "Environment is consistent and ready for use."
        exit 0
    else
        echo -e "${YELLOW}⚠ Deployment verified with minor warnings${NC}"
        echo ""
        echo "Deployment is functional but some optional checks failed."
        echo "Review warnings above for details."
        exit 0
    fi
else
    echo -e "${RED}✗ Deployment verification failed${NC}"
    echo ""
    echo "Please address the failed checks above."
    echo "Run ./scripts/status.sh for more details."
    exit 1
fi
