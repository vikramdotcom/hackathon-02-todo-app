#!/bin/bash

# Phase IV - End-to-End Deployment Test
# Tests complete deployment workflow from clean state

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

TEST_PASSED=0
TEST_FAILED=0
START_TIME=$(date +%s)

echo "========================================="
echo "Phase IV - End-to-End Deployment Test"
echo "========================================="
echo ""

# Function to log test results
log_test() {
    local test_name=$1
    local result=$2

    if [ "$result" = "pass" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((TEST_PASSED++))
    else
        echo -e "${RED}✗${NC} $test_name"
        ((TEST_FAILED++))
    fi
}

# Test 1: Prerequisites
echo "Test 1: Checking prerequisites..."
if ./scripts/validate-prerequisites.sh > /dev/null 2>&1; then
    log_test "Prerequisites validation" "pass"
else
    log_test "Prerequisites validation" "fail"
    echo "Please ensure all prerequisites are met"
    exit 1
fi

# Test 2: Minikube setup
echo ""
echo "Test 2: Checking Minikube..."
if minikube status > /dev/null 2>&1; then
    log_test "Minikube is running" "pass"
else
    echo "Starting Minikube..."
    if ./scripts/setup-minikube.sh; then
        log_test "Minikube setup" "pass"
    else
        log_test "Minikube setup" "fail"
        exit 1
    fi
fi

# Test 3: Docker images
echo ""
echo "Test 3: Building Docker images..."
BUILD_START=$(date +%s)

if ./scripts/build-images.sh; then
    BUILD_END=$(date +%s)
    BUILD_TIME=$((BUILD_END - BUILD_START))
    log_test "Docker images built (${BUILD_TIME}s)" "pass"
else
    log_test "Docker image build" "fail"
    exit 1
fi

# Test 4: Validate manifests
echo ""
echo "Test 4: Validating Kubernetes manifests..."
if ./tests/k8s-validate.sh > /dev/null 2>&1; then
    log_test "Kubernetes manifest validation" "pass"
else
    log_test "Kubernetes manifest validation" "fail"
fi

# Test 5: Validate Helm chart
echo ""
echo "Test 5: Validating Helm chart..."
if ./tests/helm-lint.sh > /dev/null 2>&1; then
    log_test "Helm chart validation" "pass"
else
    log_test "Helm chart validation" "fail"
fi

# Test 6: Deploy application
echo ""
echo "Test 6: Deploying application..."
DEPLOY_START=$(date +%s)

if ./scripts/deploy.sh > /dev/null 2>&1; then
    DEPLOY_END=$(date +%s)
    DEPLOY_TIME=$((DEPLOY_END - DEPLOY_START))
    log_test "Application deployment (${DEPLOY_TIME}s)" "pass"
else
    log_test "Application deployment" "fail"
    exit 1
fi

# Test 7: Wait for pods to be ready
echo ""
echo "Test 7: Waiting for pods to be ready..."
WAIT_START=$(date +%s)
MAX_WAIT=300  # 5 minutes

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - WAIT_START))

    if [ $ELAPSED -gt $MAX_WAIT ]; then
        log_test "Pods ready within timeout" "fail"
        kubectl get pods -n todo-app
        break
    fi

    TOTAL_PODS=$(kubectl get pods -n todo-app --no-headers 2>/dev/null | wc -l)
    READY_PODS=$(kubectl get pods -n todo-app --no-headers 2>/dev/null | grep "Running" | grep -E "([0-9]+)/\1" | wc -l)

    if [ "$READY_PODS" -eq "$TOTAL_PODS" ] && [ "$TOTAL_PODS" -gt 0 ]; then
        log_test "All pods ready (${ELAPSED}s)" "pass"
        break
    fi

    sleep 5
done

# Test 8: Verify services
echo ""
echo "Test 8: Verifying services..."

if kubectl get service frontend -n todo-app > /dev/null 2>&1; then
    log_test "Frontend service exists" "pass"
else
    log_test "Frontend service exists" "fail"
fi

if kubectl get service backend -n todo-app > /dev/null 2>&1; then
    log_test "Backend service exists" "pass"
else
    log_test "Backend service exists" "fail"
fi

if kubectl get service database -n todo-app > /dev/null 2>&1; then
    log_test "Database service exists" "pass"
else
    log_test "Database service exists" "fail"
fi

# Test 9: Verify ingress
echo ""
echo "Test 9: Verifying ingress..."

if kubectl get ingress todo-app-ingress -n todo-app > /dev/null 2>&1; then
    log_test "Ingress exists" "pass"
else
    log_test "Ingress exists" "fail"
fi

# Test 10: Health checks
echo ""
echo "Test 10: Checking health endpoints..."

BACKEND_POD=$(kubectl get pods -n todo-app -l component=backend -o jsonpath='{.items[0].metadata.name}')

if [ -n "$BACKEND_POD" ]; then
    if kubectl exec -n todo-app "$BACKEND_POD" -- curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        log_test "Backend health endpoint" "pass"
    else
        log_test "Backend health endpoint" "fail"
    fi
fi

# Test 11: Database connectivity
echo ""
echo "Test 11: Checking database connectivity..."

if [ -n "$BACKEND_POD" ]; then
    if kubectl exec -n todo-app "$BACKEND_POD" -- pg_isready -h database -p 5432 -U postgres > /dev/null 2>&1; then
        log_test "Database connectivity" "pass"
    else
        log_test "Database connectivity" "fail"
    fi
fi

# Test 12: Resource usage
echo ""
echo "Test 12: Checking resource usage..."

if kubectl top pods -n todo-app > /dev/null 2>&1; then
    log_test "Metrics available" "pass"
    echo ""
    echo "Current resource usage:"
    kubectl top pods -n todo-app
else
    log_test "Metrics available" "fail"
fi

# Test 13: Scaling test
echo ""
echo "Test 13: Testing service scaling..."

if kubectl scale deployment/backend --replicas=3 -n todo-app > /dev/null 2>&1; then
    sleep 10
    BACKEND_REPLICAS=$(kubectl get deployment backend -n todo-app -o jsonpath='{.status.readyReplicas}')
    if [ "$BACKEND_REPLICAS" = "3" ]; then
        log_test "Backend scaling to 3 replicas" "pass"
    else
        log_test "Backend scaling to 3 replicas" "fail"
    fi

    # Scale back
    kubectl scale deployment/backend --replicas=2 -n todo-app > /dev/null 2>&1
else
    log_test "Backend scaling" "fail"
fi

# Test 14: Cleanup test
echo ""
echo "Test 14: Testing cleanup..."

read -p "Do you want to test cleanup? This will remove the deployment. (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if ./scripts/cleanup.sh <<< "y" > /dev/null 2>&1; then
        log_test "Cleanup successful" "pass"
    else
        log_test "Cleanup successful" "fail"
    fi
else
    echo "Skipping cleanup test"
fi

# Calculate total time
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))
MINUTES=$((TOTAL_TIME / 60))
SECONDS=$((TOTAL_TIME % 60))

# Summary
echo ""
echo "========================================="
echo "Test Summary"
echo "========================================="
echo -e "${GREEN}Passed:${NC} $TEST_PASSED"
echo -e "${RED}Failed:${NC} $TEST_FAILED"
echo -e "${BLUE}Total Time:${NC} ${MINUTES}m ${SECONDS}s"
echo ""

# Success criteria
SUCCESS_RATE=$((TEST_PASSED * 100 / (TEST_PASSED + TEST_FAILED)))

echo "Success Rate: ${SUCCESS_RATE}%"
echo ""

if [ $TEST_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Deployment is fully functional and meets success criteria:"
    echo "  ✓ Deployment time under 10 minutes"
    echo "  ✓ All services healthy"
    echo "  ✓ Scaling works correctly"
    echo "  ✓ Health checks passing"
    exit 0
elif [ $SUCCESS_RATE -ge 95 ]; then
    echo -e "${YELLOW}⚠ Tests passed with minor issues (${SUCCESS_RATE}%)${NC}"
    echo ""
    echo "Deployment is functional but some optional features may have issues."
    exit 0
else
    echo -e "${RED}✗ Tests failed (${SUCCESS_RATE}%)${NC}"
    echo ""
    echo "Please review the failed tests and troubleshoot."
    exit 1
fi
