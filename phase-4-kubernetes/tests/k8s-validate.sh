#!/bin/bash

# Phase IV - Kubernetes Manifest Validation Script
# Validates Kubernetes manifests syntax and best practices

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

K8S_PATH="k8s"
PASSED=0
FAILED=0
WARNINGS=0

echo "========================================="
echo "Kubernetes Manifest Validation"
echo "========================================="
echo ""

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}✗ kubectl is not installed${NC}"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

echo -e "${GREEN}✓ kubectl is installed${NC}"
echo ""

# Check if manifest directory exists
if [ ! -d "$K8S_PATH" ]; then
    echo -e "${RED}✗ Manifest directory not found: $K8S_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Manifest directory found${NC}"
echo ""

# Validate each manifest file
echo "========================================="
echo "1. Manifest Syntax Validation"
echo "========================================="
echo ""

for manifest in "$K8S_PATH"/*.yaml; do
    if [ -f "$manifest" ]; then
        echo "Validating $(basename $manifest)..."
        if kubectl apply --dry-run=client -f "$manifest" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $(basename $manifest) is valid${NC}"
            ((PASSED++))
        else
            echo -e "${RED}✗ $(basename $manifest) is invalid${NC}"
            kubectl apply --dry-run=client -f "$manifest" 2>&1 | head -5
            ((FAILED++))
        fi
        echo ""
    fi
done

# Check for required manifests
echo "========================================="
echo "2. Required Manifests Check"
echo "========================================="
echo ""

REQUIRED_MANIFESTS=(
    "namespace.yaml"
    "configmap.yaml"
    "frontend-deployment.yaml"
    "frontend-service.yaml"
    "backend-deployment.yaml"
    "backend-service.yaml"
    "database-deployment.yaml"
    "database-service.yaml"
    "ingress.yaml"
)

for manifest in "${REQUIRED_MANIFESTS[@]}"; do
    if [ -f "$K8S_PATH/$manifest" ]; then
        echo -e "${GREEN}✓ Found: $manifest${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ Missing: $manifest${NC}"
        ((WARNINGS++))
    fi
done

echo ""

# Check for best practices
echo "========================================="
echo "3. Best Practices Check"
echo "========================================="
echo ""

# Check for resource limits
echo "Checking resource limits..."
for deployment in "$K8S_PATH"/*-deployment.yaml; do
    if [ -f "$deployment" ]; then
        if grep -q "resources:" "$deployment" && grep -q "limits:" "$deployment"; then
            echo -e "${GREEN}✓ $(basename $deployment) has resource limits${NC}"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠ $(basename $deployment) missing resource limits${NC}"
            ((WARNINGS++))
        fi
    fi
done

echo ""

# Check for health probes
echo "Checking health probes..."
for deployment in "$K8S_PATH"/*-deployment.yaml; do
    if [ -f "$deployment" ]; then
        if grep -q "livenessProbe:" "$deployment" && grep -q "readinessProbe:" "$deployment"; then
            echo -e "${GREEN}✓ $(basename $deployment) has health probes${NC}"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠ $(basename $deployment) missing health probes${NC}"
            ((WARNINGS++))
        fi
    fi
done

echo ""

# Check for labels
echo "Checking labels..."
for manifest in "$K8S_PATH"/*.yaml; do
    if [ -f "$manifest" ]; then
        if grep -q "labels:" "$manifest"; then
            echo -e "${GREEN}✓ $(basename $manifest) has labels${NC}"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠ $(basename $manifest) missing labels${NC}"
            ((WARNINGS++))
        fi
    fi
done

echo ""

# Check for security contexts
echo "========================================="
echo "4. Security Check"
echo "========================================="
echo ""

for deployment in "$K8S_PATH"/*-deployment.yaml; do
    if [ -f "$deployment" ]; then
        if grep -q "securityContext:" "$deployment"; then
            echo -e "${GREEN}✓ $(basename $deployment) has security context${NC}"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠ $(basename $deployment) missing security context${NC}"
            ((WARNINGS++))
        fi
    fi
done

echo ""

# Summary
echo "========================================="
echo "Validation Summary"
echo "========================================="
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✓ All validations passed!${NC}"
    else
        echo -e "${YELLOW}⚠ Validations passed with warnings${NC}"
    fi
    exit 0
else
    echo -e "${RED}✗ Some validations failed${NC}"
    exit 1
fi
