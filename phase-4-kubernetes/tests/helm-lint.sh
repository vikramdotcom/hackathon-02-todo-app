#!/bin/bash

# Phase IV - Helm Chart Validation Script
# Validates Helm chart syntax and best practices

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CHART_PATH="helm/todo-app"
PASSED=0
FAILED=0
WARNINGS=0

echo "========================================="
echo "Helm Chart Validation"
echo "========================================="
echo ""

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}✗ Helm is not installed${NC}"
    echo "Please install Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi

echo -e "${GREEN}✓ Helm is installed${NC}"
echo ""

# Check if chart directory exists
if [ ! -d "$CHART_PATH" ]; then
    echo -e "${RED}✗ Chart directory not found: $CHART_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Chart directory found${NC}"
echo ""

# Lint the chart
echo "========================================="
echo "1. Helm Lint"
echo "========================================="
echo ""

if helm lint "$CHART_PATH"; then
    echo -e "${GREEN}✓ Helm lint passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Helm lint failed${NC}"
    ((FAILED++))
fi

echo ""

# Lint with values files
echo "========================================="
echo "2. Lint with Values Files"
echo "========================================="
echo ""

for values_file in "$CHART_PATH/values-dev.yaml" "$CHART_PATH/values-test.yaml"; do
    if [ -f "$values_file" ]; then
        echo "Linting with $(basename $values_file)..."
        if helm lint "$CHART_PATH" -f "$values_file"; then
            echo -e "${GREEN}✓ Lint passed with $(basename $values_file)${NC}"
            ((PASSED++))
        else
            echo -e "${RED}✗ Lint failed with $(basename $values_file)${NC}"
            ((FAILED++))
        fi
        echo ""
    fi
done

# Template rendering
echo "========================================="
echo "3. Template Rendering"
echo "========================================="
echo ""

echo "Rendering templates..."
if helm template test-release "$CHART_PATH" > /dev/null; then
    echo -e "${GREEN}✓ Template rendering successful${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Template rendering failed${NC}"
    ((FAILED++))
fi

echo ""

# Check required files
echo "========================================="
echo "4. Required Files Check"
echo "========================================="
echo ""

REQUIRED_FILES=(
    "$CHART_PATH/Chart.yaml"
    "$CHART_PATH/values.yaml"
    "$CHART_PATH/templates/_helpers.tpl"
    "$CHART_PATH/templates/NOTES.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ Found: $(basename $file)${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Missing: $(basename $file)${NC}"
        ((FAILED++))
    fi
done

echo ""

# Check Chart.yaml
echo "========================================="
echo "5. Chart.yaml Validation"
echo "========================================="
echo ""

if [ -f "$CHART_PATH/Chart.yaml" ]; then
    # Check apiVersion
    if grep -q "apiVersion: v2" "$CHART_PATH/Chart.yaml"; then
        echo -e "${GREEN}✓ API version is v2${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ API version is not v2${NC}"
        ((FAILED++))
    fi

    # Check name
    if grep -q "name:" "$CHART_PATH/Chart.yaml"; then
        echo -e "${GREEN}✓ Chart name is defined${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Chart name is missing${NC}"
        ((FAILED++))
    fi

    # Check version
    if grep -q "version:" "$CHART_PATH/Chart.yaml"; then
        echo -e "${GREEN}✓ Chart version is defined${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Chart version is missing${NC}"
        ((FAILED++))
    fi
fi

echo ""

# Check values.yaml
echo "========================================="
echo "6. values.yaml Validation"
echo "========================================="
echo ""

if [ -f "$CHART_PATH/values.yaml" ]; then
    # Check if valid YAML
    if python3 -c "import yaml; yaml.safe_load(open('$CHART_PATH/values.yaml'))" 2>/dev/null; then
        echo -e "${GREEN}✓ values.yaml is valid YAML${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ values.yaml is not valid YAML${NC}"
        ((FAILED++))
    fi

    # Check for common keys
    for key in "global" "frontend" "backend" "database"; do
        if grep -q "$key:" "$CHART_PATH/values.yaml"; then
            echo -e "${GREEN}✓ Found key: $key${NC}"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠ Missing key: $key${NC}"
            ((WARNINGS++))
        fi
    done
fi

echo ""

# Check templates
echo "========================================="
echo "7. Template Files Check"
echo "========================================="
echo ""

TEMPLATE_FILES=(
    "frontend-deployment.yaml"
    "frontend-service.yaml"
    "backend-deployment.yaml"
    "backend-service.yaml"
    "database-deployment.yaml"
    "database-service.yaml"
    "ingress.yaml"
)

for template in "${TEMPLATE_FILES[@]}"; do
    if [ -f "$CHART_PATH/templates/$template" ]; then
        echo -e "${GREEN}✓ Found: $template${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Missing: $template${NC}"
        ((FAILED++))
    fi
done

echo ""

# Dry-run install
echo "========================================="
echo "8. Dry-run Install"
echo "========================================="
echo ""

echo "Performing dry-run install..."
if helm install test-release "$CHART_PATH" --dry-run --debug > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Dry-run install successful${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Dry-run install failed${NC}"
    ((FAILED++))
fi

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
    echo -e "${GREEN}✓ All validations passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some validations failed${NC}"
    exit 1
fi
