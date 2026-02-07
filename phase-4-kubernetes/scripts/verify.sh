#!/bin/bash

# Phase IV - End-to-End Verification Script
# Validates the complete deployment and functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

echo "========================================="
echo "Phase IV - End-to-End Verification"
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

# 1. Prerequisites
echo "========================================="
echo "1. Prerequisites"
echo "========================================="
echo ""

check "Minikube running" "minikube status"
check "kubectl configured" "kubectl cluster-info"
check "Docker daemon" "docker info"

echo ""

# 2. Namespace and Resources
echo "========================================="
echo "2. Namespace and Resources"
echo "========================================="
echo ""

check "Namespace exists" "kubectl get namespace todo-app"
check "ConfigMap exists" "kubectl get configmap todo-app-config -n todo-app"
check "Secret exists" "kubectl get secret todo-app-secrets -n todo-app"
check "PVC exists" "kubectl get pvc postgres-pvc -n todo-app"
check "PVC bound" "kubectl get pvc postgres-pvc -n todo-app -o jsonpath='{.status.phase}' | grep -q Bound"

echo ""

# 3. Deployments
echo "========================================="
echo "3. Deployments"
echo "========================================="
echo ""

check "Frontend deployment exists" "kubectl get deployment frontend -n todo-app"
check "Backend deployment exists" "kubectl get deployment backend -n todo-app"
check "Database deployment exists" "kubectl get deployment database -n todo-app"

echo ""

# 4. Services
echo "========================================="
echo "4. Services"
echo "========================================="
echo ""

check "Frontend service exists" "kubectl get service frontend -n todo-app"
check "Backend service exists" "kubectl get service backend -n todo-app"
check "Database service exists" "kubectl get service database -n todo-app"

echo ""

# 5. Ingress
echo "========================================="
echo "5. Ingress"
echo "========================================="
echo ""

check "Ingress exists" "kubectl get ingress todo-app-ingress -n todo-app"
check "Ingress has address" "kubectl get ingress todo-app-ingress -n todo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}' | grep -q ."

echo ""

# 6. Pod Health
echo "========================================="
echo "6. Pod Health"
echo "========================================="
echo ""

# Get pod counts
FRONTEND_DESIRED=$(kubectl get deployment frontend -n todo-app -o jsonpath='{.spec.replicas}')
FRONTEND_READY=$(kubectl get deployment frontend -n todo-app -o jsonpath='{.status.readyReplicas}')
BACKEND_DESIRED=$(kubectl get deployment backend -n todo-app -o jsonpath='{.spec.replicas}')
BACKEND_READY=$(kubectl get deployment backend -n todo-app -o jsonpath='{.status.readyReplicas}')
DATABASE_DESIRED=$(kubectl get deployment database -n todo-app -o jsonpath='{.spec.replicas}')
DATABASE_READY=$(kubectl get deployment database -n todo-app -o jsonpath='{.status.readyReplicas}')

echo -n "Frontend pods ready... "
if [ "$FRONTEND_READY" = "$FRONTEND_DESIRED" ]; then
    echo -e "${GREEN}✓${NC} ($FRONTEND_READY/$FRONTEND_DESIRED)"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} ($FRONTEND_READY/$FRONTEND_DESIRED)"
    ((FAILED++))
fi

echo -n "Backend pods ready... "
if [ "$BACKEND_READY" = "$BACKEND_DESIRED" ]; then
    echo -e "${GREEN}✓${NC} ($BACKEND_READY/$BACKEND_DESIRED)"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} ($BACKEND_READY/$BACKEND_DESIRED)"
    ((FAILED++))
fi

echo -n "Database pods ready... "
if [ "$DATABASE_READY" = "$DATABASE_DESIRED" ]; then
    echo -e "${GREEN}✓${NC} ($DATABASE_READY/$DATABASE_DESIRED)"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} ($DATABASE_READY/$DATABASE_DESIRED)"
    ((FAILED++))
fi

echo ""

# 7. Health Endpoints
echo "========================================="
echo "7. Health Endpoints"
echo "========================================="
echo ""

# Get a backend pod
BACKEND_POD=$(kubectl get pods -n todo-app -l component=backend -o jsonpath='{.items[0].metadata.name}')

if [ -n "$BACKEND_POD" ]; then
    echo -n "Backend health endpoint... "
    if kubectl exec -n todo-app "$BACKEND_POD" -- curl -sf http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
    fi
fi

# Get a frontend pod
FRONTEND_POD=$(kubectl get pods -n todo-app -l component=frontend -o jsonpath='{.items[0].metadata.name}')

if [ -n "$FRONTEND_POD" ]; then
    echo -n "Frontend health endpoint... "
    if kubectl exec -n todo-app "$FRONTEND_POD" -- wget -q -O- http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
    fi
fi

echo ""

# 8. Database Connectivity
echo "========================================="
echo "8. Database Connectivity"
echo "========================================="
echo ""

if [ -n "$BACKEND_POD" ]; then
    echo -n "Backend can connect to database... "
    if kubectl exec -n todo-app "$BACKEND_POD" -- pg_isready -h database -p 5432 -U postgres > /dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
    fi
fi

echo ""

# 9. Ingress Accessibility
echo "========================================="
echo "9. Ingress Accessibility"
echo "========================================="
echo ""

MINIKUBE_IP=$(minikube ip)

echo -n "Hosts file entry... "
if grep -q "$MINIKUBE_IP.*todo.local" /etc/hosts 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} (Add: $MINIKUBE_IP todo.local to /etc/hosts)"
    ((WARNINGS++))
fi

warn "Frontend accessible via Ingress" "curl -sf http://todo.local -o /dev/null"
warn "Backend accessible via Ingress" "curl -sf http://todo.local/api/health -o /dev/null"

echo ""

# 10. Resource Usage
echo "========================================="
echo "10. Resource Usage"
echo "========================================="
echo ""

echo -n "Metrics server available... "
if kubectl top nodes &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))

    echo ""
    echo "Current resource usage:"
    kubectl top pods -n todo-app
else
    echo -e "${YELLOW}⚠${NC} (Metrics not available yet)"
    ((WARNINGS++))
fi

echo ""

# 11. Logs Check
echo "========================================="
echo "11. Logs Check"
echo "========================================="
echo ""

echo -n "No crash loops... "
CRASH_LOOPS=$(kubectl get pods -n todo-app -o jsonpath='{.items[*].status.containerStatuses[*].restartCount}' | tr ' ' '\n' | awk '{s+=$1} END {print s}')
if [ "$CRASH_LOOPS" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} (0 restarts)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} ($CRASH_LOOPS total restarts)"
    ((WARNINGS++))
fi

echo -n "No error events... "
ERROR_EVENTS=$(kubectl get events -n todo-app --field-selector type=Warning | grep -c . || echo 0)
if [ "$ERROR_EVENTS" -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} ($ERROR_EVENTS warning events)"
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

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✓ All checks passed!${NC}"
        echo ""
        echo "Your Todo App is fully deployed and operational."
        echo ""
        echo "Access the application:"
        echo "  Frontend: http://todo.local"
        echo "  Backend API: http://todo.local/api"
        echo "  Health Check: http://todo.local/api/health"
        exit 0
    else
        echo -e "${YELLOW}⚠ Deployment successful with warnings${NC}"
        echo ""
        echo "The application is deployed but some optional features may not be available."
        echo "Review the warnings above and address them if needed."
        exit 0
    fi
else
    echo -e "${RED}✗ Deployment has issues${NC}"
    echo ""
    echo "Please review the failed checks above and troubleshoot:"
    echo "  1. Check pod logs: kubectl logs <pod-name> -n todo-app"
    echo "  2. Describe resources: kubectl describe <resource> -n todo-app"
    echo "  3. Check events: kubectl get events -n todo-app"
    echo "  4. Review TROUBLESHOOTING.md for common issues"
    exit 1
fi
