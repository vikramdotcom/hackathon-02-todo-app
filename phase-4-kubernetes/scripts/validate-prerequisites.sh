#!/bin/bash

# Phase IV - Prerequisite Validation Script (Linux/macOS)
# Validates that all required tools are installed and configured

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

echo "========================================="
echo "Phase IV - Prerequisite Validation"
echo "========================================="
echo ""

# Function to check if command exists
check_command() {
    local cmd=$1
    local name=$2
    local min_version=$3

    if command -v "$cmd" &> /dev/null; then
        local version=$($cmd --version 2>&1 | head -n 1)
        echo -e "${GREEN}✓${NC} $name installed: $version"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $name not found"
        echo "  Install from: $4"
        ((FAILED++))
        return 1
    fi
}

# Function to check Docker daemon
check_docker_daemon() {
    if docker info &> /dev/null; then
        echo -e "${GREEN}✓${NC} Docker daemon running"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} Docker daemon not running"
        echo "  Start Docker Desktop or run: sudo systemctl start docker"
        ((FAILED++))
        return 1
    fi
}

# Function to check system resources
check_resources() {
    # Check available RAM (in GB)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        local total_ram=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    else
        # Linux
        local total_ram=$(free -g | awk '/^Mem:/{print $2}')
    fi

    if [ "$total_ram" -ge 8 ]; then
        echo -e "${GREEN}✓${NC} System RAM: ${total_ram}GB (minimum 8GB)"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} System RAM: ${total_ram}GB (recommended: 8GB+)"
        echo "  You may experience performance issues"
        ((PASSED++))
    fi

    # Check available disk space (in GB)
    local free_space=$(df -BG . | awk 'NR==2 {print int($4)}')

    if [ "$free_space" -ge 20 ]; then
        echo -e "${GREEN}✓${NC} Free disk space: ${free_space}GB (minimum 20GB)"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Free disk space: ${free_space}GB (minimum 20GB required)"
        echo "  Free up disk space before proceeding"
        ((FAILED++))
    fi
}

# Check required tools
echo "Checking required tools..."
echo ""

check_command "docker" "Docker" "24.0" "https://www.docker.com/get-started"
check_command "minikube" "Minikube" "1.30" "https://minikube.sigs.k8s.io/docs/start/"
check_command "kubectl" "kubectl" "1.28" "https://kubernetes.io/docs/tasks/tools/"
check_command "helm" "Helm" "3.12" "https://helm.sh/docs/intro/install/"

echo ""
echo "Checking Docker daemon..."
echo ""

check_docker_daemon

echo ""
echo "Checking system resources..."
echo ""

check_resources

echo ""
echo "========================================="
echo "Validation Summary"
echo "========================================="
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All prerequisites met!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: ./scripts/setup-minikube.sh"
    echo "  2. Run: ./scripts/deploy.sh"
    exit 0
else
    echo -e "${RED}✗ Some prerequisites are missing${NC}"
    echo ""
    echo "Please install missing tools and try again."
    exit 1
fi
