#!/bin/bash

# Phase IV - Health Check Script (Linux/macOS)
# Comprehensive health check for all components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

NAMESPACE="todo-app"
PASSED=0
FAILED=0
WARNINGS=0

echo "========================================="
echo "Health Check - Todo App"
echo "========================================="
echo ""

# Function to check and report
check() {
    local name=$1
    local command=$2
    local error_msg=$3

    echo -n "Checking $name... "

    if eval "$command" &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC}"
        if [ -n "$error_msg" ]; then
            echo "  Error: $error_msg"
        fi
        ((FAILED++))
        return 1
    fi
}

# Function for warnings
warn() {
    local name=$1
    local command=$2
    local warning_msg=$3

    echo -n "Checking $name... "

    if eval "$command" &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠${NC}"
        if [ -n "$warning_msg" ]; then
            echo "  Warning: $warning_msg"
        fi
        ((WARNINGS++))
        return 1
    fi
}

# 1. Cluster Health
echo "========================================="
echo "1. Cluster Health"
echo "========================================="
echo ""

check "Minikube running" "minikube status" "Start Minikube with: ./scripts/setup-minikube.sh"
check "kubectl configured" "kubectl cluster-info" "Check kubectl configuration"
check "Metrics server available" "kubectl top nodes" "Enable with: minikube addons enable metrics-server"

echo ""

# 2. Namespace Health
echo "========================================="
echo "2. Namespace Health"
echo "========================================="
echo ""

if kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${GREEN}✓${NC} Namespace exists"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Namespace not found"
    echo "  Error: Deploy the application first"
    ((FAILED++))
    exit 1
fi

echo ""

# 3. Deployment Health
echo "========================================="
echo "3. Deployment Health"
echo "========================================="
echo ""

# Check deployments exist
check "Frontend deployment exists" "kubectl get deployment frontend -n $NAMESPACE" "Deploy with: ./scripts/deploy.sh"
check "Backend deployment exists" "kubectl get deployment backend -n $NAMESPACE" "Deploy with: ./scripts/deploy.sh"
check "Database deployment exists" "kubectl get deployment database -n $NAMESPACE" "Deploy with: ./scripts/deploy.sh"

# Check deployment health
FRONTEND_DESIRED=$(kubectl get deployment frontend -n $NAMESPACE -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
FRONTEND_READY=$(kubectl get deployment frontend -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
BACKEND_DESIRED=$(kubectl get deployment backend -n $NAMESPACE -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
BACKEND_READY=$(kubectl get deployment backend -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
DATABASE_DESIRED=$(kubectl get deployment database -n $NAMESPACE -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
DATABASE_READY=$(kubectl get deployment database -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")

echo ""
echo -e "${BLUE}Deployment Status:${NC}"
echo "  Frontend: $FRONTEND_READY/$FRONTEND_DESIRED ready"
echo "  Backend: $BACKEND_READY/$BACKEND_DESIRED ready"
echo "  Database: $DATABASE_READY/$DATABASE_DESIRED ready"
echo ""

if [ "$FRONTEND_READY" = "$FRONTEND_DESIRED" ] && [ "$FRONTEND_DESIRED" != "0" ]; then
    echo -e "${GREEN}✓${NC} Frontend deployment healthy"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Frontend deployment unhealthy"
    echo "  Error: Check logs with: ./scripts/view-logs.sh frontend"
    ((FAILED++))
fi

if [ "$BACKEND_READY" = "$BACKEND_DESIRED" ] && [ "$BACKEND_DESIRED" != "0" ]; then
    echo -e "${GREEN}✓${NC} Backend deployment healthy"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Backend deployment unhealthy"
    echo "  Error: Check logs with: ./scripts/view-logs.sh backend"
    ((FAILED++))
fi

if [ "$DATABASE_READY" = "$DATABASE_DESIRED" ] && [ "$DATABASE_DESIRED" != "0" ]; then
    echo -e "${GREEN}✓${NC} Database deployment healthy"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Database deployment unhealthy"
    echo "  Error: Check logs with: ./scripts/view-logs.sh database"
    ((FAILED++))
fi

echo ""

# 4. Pod Health
echo "========================================="
echo "4. Pod Health"
echo "========================================="
echo ""

# Check for crash loops
CRASH_LOOPS=$(kubectl get pods -n $NAMESPACE -o jsonpath='{.items[*].status.containerStatuses[*].restartCount}' 2>/dev/null | tr ' ' '\n' | awk '{s+=$1} END {print s}')
CRASH_LOOPS=${CRASH_LOOPS:-0}

if [ "$CRASH_LOOPS" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No crash loops detected"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Crash loops detected ($CRASH_LOOPS total restarts)"
    echo "  Warning: Check pod logs for errors"
    ((WARNINGS++))
fi

# Check for pending pods
PENDING_PODS=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase=Pending --no-headers 2>/dev/null | wc -l)

if [ "$PENDING_PODS" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No pending pods"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Pending pods detected ($PENDING_PODS pods)"
    echo "  Error: Check with: kubectl describe pods -n $NAMESPACE"
    ((FAILED++))
fi

# Check for failed pods
FAILED_PODS=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase=Failed --no-headers 2>/dev/null | wc -l)

if [ "$FAILED_PODS" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No failed pods"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Failed pods detected ($FAILED_PODS pods)"
    echo "  Error: Check with: kubectl get pods -n $NAMESPACE"
    ((FAILED++))
fi

echo ""

# 5. Service Health
echo "========================================="
echo "5. Service Health"
echo "========================================="
echo ""

check "Frontend service exists" "kubectl get service frontend -n $NAMESPACE" "Check deployment"
check "Backend service exists" "kubectl get service backend -n $NAMESPACE" "Check deployment"
check "Database service exists" "kubectl get service database -n $NAMESPACE" "Check deployment"

# Check service endpoints
FRONTEND_ENDPOINTS=$(kubectl get endpoints frontend -n $NAMESPACE -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null | wc -w)
BACKEND_ENDPOINTS=$(kubectl get endpoints backend -n $NAMESPACE -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null | wc -w)
DATABASE_ENDPOINTS=$(kubectl get endpoints database -n $NAMESPACE -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null | wc -w)

echo ""
echo -e "${BLUE}Service Endpoints:${NC}"
echo "  Frontend: $FRONTEND_ENDPOINTS endpoints"
echo "  Backend: $BACKEND_ENDPOINTS endpoints"
echo "  Database: $DATABASE_ENDPOINTS endpoints"
echo ""

if [ "$FRONTEND_ENDPOINTS" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Frontend service has endpoints"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Frontend service has no endpoints"
    ((FAILED++))
fi

if [ "$BACKEND_ENDPOINTS" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Backend service has endpoints"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Backend service has no endpoints"
    ((FAILED++))
fi

if [ "$DATABASE_ENDPOINTS" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Database service has endpoints"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Database service has no endpoints"
    ((FAILED++))
fi

echo ""

# 6. Application Health
echo "========================================="
echo "6. Application Health"
echo "========================================="
echo ""

# Test backend health endpoint
BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l component=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -n "$BACKEND_POD" ]; then
    if kubectl exec -n $NAMESPACE "$BACKEND_POD" -- curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend health endpoint responding"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Backend health endpoint not responding"
        echo "  Error: Check backend logs"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗${NC} No backend pod found"
    ((FAILED++))
fi

# Test database connectivity
if [ -n "$BACKEND_POD" ]; then
    if kubectl exec -n $NAMESPACE "$BACKEND_POD" -- pg_isready -h database -p 5432 -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Database connectivity from backend"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Database connectivity failed"
        echo "  Error: Check database logs and secrets"
        ((FAILED++))
    fi
fi

echo ""

# 7. Ingress Health
echo "========================================="
echo "7. Ingress Health"
echo "========================================="
echo ""

check "Ingress exists" "kubectl get ingress todo-app-ingress -n $NAMESPACE" "Check deployment"

# Check Ingress controller
warn "Ingress controller running" "kubectl get pods -n ingress-nginx -l app.kubernetes.io/component=controller" "Enable with: minikube addons enable ingress"

# Check hosts file
MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "")
if [ -n "$MINIKUBE_IP" ]; then
    if grep -q "$MINIKUBE_IP.*todo.local" /etc/hosts 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Hosts file configured"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} Hosts file not configured"
        echo "  Warning: Add: $MINIKUBE_IP todo.local to /etc/hosts"
        ((WARNINGS++))
    fi
fi

echo ""

# 8. Resource Usage
echo "========================================="
echo "8. Resource Usage"
echo "========================================="
echo ""

if kubectl top nodes &> /dev/null; then
    echo -e "${GREEN}✓${NC} Metrics available"
    ((PASSED++))

    echo ""
    echo -e "${BLUE}Current Resource Usage:${NC}"
    kubectl top pods -n $NAMESPACE 2>/dev/null || echo "  No pod metrics available yet"
else
    echo -e "${YELLOW}⚠${NC} Metrics not available"
    echo "  Warning: Wait for metrics-server to be ready"
    ((WARNINGS++))
fi

echo ""

# Summary
echo "========================================="
echo "Health Check Summary"
echo "========================================="
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

# Recommendations
if [ $FAILED -gt 0 ] || [ $WARNINGS -gt 0 ]; then
    echo "========================================="
    echo "Troubleshooting Recommendations"
    echo "========================================="
    echo ""

    if [ $FAILED -gt 0 ]; then
        echo "Critical issues detected. Try these steps:"
        echo "  1. Check pod logs: ./scripts/view-logs.sh all"
        echo "  2. Check pod status: kubectl get pods -n $NAMESPACE"
        echo "  3. Describe failed pods: kubectl describe pod <pod-name> -n $NAMESPACE"
        echo "  4. Check events: kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'"
        echo "  5. Review troubleshooting guide: TROUBLESHOOTING.md"
        echo ""
    fi

    if [ $WARNINGS -gt 0 ]; then
        echo "Warnings detected. Consider these actions:"
        echo "  1. Wait for metrics-server to be ready"
        echo "  2. Configure hosts file for Ingress access"
        echo "  3. Check for pod restarts and investigate causes"
        echo ""
    fi
fi

# Exit code
if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✓ All health checks passed!${NC}"
        echo ""
        echo "Your Todo App is healthy and ready to use."
        echo "Access at: http://todo.local"
        exit 0
    else
        echo -e "${YELLOW}⚠ Health checks passed with warnings${NC}"
        echo ""
        echo "The application is functional but some optional features may have issues."
        exit 0
    fi
else
    echo -e "${RED}✗ Health checks failed${NC}"
    echo ""
    echo "Please address the issues above before using the application."
    exit 1
fi
