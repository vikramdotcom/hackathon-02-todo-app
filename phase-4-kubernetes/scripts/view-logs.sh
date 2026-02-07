#!/bin/bash

# Phase IV - Log Viewing Helper Script (Linux/macOS)
# Simplified log viewing for troubleshooting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

NAMESPACE="todo-app"
COMPONENT=""
FOLLOW=false
TAIL_LINES=100
PREVIOUS=false

# Usage function
usage() {
    echo "Usage: $0 [options] <component>"
    echo ""
    echo "Components:"
    echo "  frontend   - View frontend logs"
    echo "  backend    - View backend logs"
    echo "  database   - View database logs"
    echo "  all        - View logs from all components"
    echo ""
    echo "Options:"
    echo "  -f, --follow       Follow log output (like tail -f)"
    echo "  -n, --lines NUM    Number of lines to show (default: 100)"
    echo "  -p, --previous     Show logs from previous container (if crashed)"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 backend                    # Show last 100 lines of backend logs"
    echo "  $0 -f frontend                # Follow frontend logs"
    echo "  $0 -n 500 backend             # Show last 500 lines"
    echo "  $0 -p backend                 # Show logs from crashed container"
    echo "  $0 all                        # Show logs from all components"
    echo ""
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -n|--lines)
            TAIL_LINES="$2"
            shift 2
            ;;
        -p|--previous)
            PREVIOUS=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            COMPONENT="$1"
            shift
            ;;
    esac
done

# Check if component specified
if [ -z "$COMPONENT" ]; then
    usage
fi

# Check if namespace exists
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${RED}Error: Namespace '$NAMESPACE' not found${NC}"
    echo "Please deploy the application first"
    exit 1
fi

echo "========================================="
echo "Log Viewer - Todo App"
echo "========================================="
echo ""

# Function to view logs
view_logs() {
    local component=$1
    local deployment_name=""

    case $component in
        frontend)
            deployment_name="frontend"
            ;;
        backend)
            deployment_name="backend"
            ;;
        database)
            deployment_name="database"
            ;;
        *)
            echo -e "${RED}Error: Unknown component '$component'${NC}"
            return 1
            ;;
    esac

    echo -e "${BLUE}Component:${NC} $component"
    echo -e "${BLUE}Namespace:${NC} $NAMESPACE"
    echo ""

    # Check if deployment exists
    if ! kubectl get deployment $deployment_name -n $NAMESPACE &> /dev/null; then
        echo -e "${RED}Error: Deployment '$deployment_name' not found${NC}"
        return 1
    fi

    # Get pod count
    POD_COUNT=$(kubectl get pods -n $NAMESPACE -l component=$component --no-headers 2>/dev/null | wc -l)

    if [ "$POD_COUNT" -eq 0 ]; then
        echo -e "${RED}Error: No pods found for component '$component'${NC}"
        return 1
    fi

    echo -e "${BLUE}Pods found:${NC} $POD_COUNT"
    echo ""

    # Build kubectl logs command
    CMD="kubectl logs"

    if [ "$FOLLOW" = true ]; then
        CMD="$CMD -f"
    fi

    if [ "$PREVIOUS" = true ]; then
        CMD="$CMD --previous"
    fi

    CMD="$CMD --tail=$TAIL_LINES"
    CMD="$CMD -l component=$component"
    CMD="$CMD -n $NAMESPACE"
    CMD="$CMD --all-containers=true"
    CMD="$CMD --prefix=true"

    echo -e "${GREEN}Viewing logs...${NC}"
    echo ""
    echo "---"
    echo ""

    # Execute command
    eval $CMD
}

# View logs based on component
case $COMPONENT in
    frontend|backend|database)
        view_logs $COMPONENT
        ;;
    all)
        echo -e "${BLUE}Viewing logs from all components${NC}"
        echo ""

        for comp in frontend backend database; do
            echo "========================================="
            echo "Component: $comp"
            echo "========================================="
            echo ""

            # Show last 50 lines for each when viewing all
            kubectl logs --tail=50 -l component=$comp -n $NAMESPACE --all-containers=true --prefix=true 2>/dev/null || echo "No logs available for $comp"

            echo ""
            echo ""
        done
        ;;
    *)
        echo -e "${RED}Error: Unknown component '$COMPONENT'${NC}"
        usage
        ;;
esac

echo ""
echo -e "${GREEN}✓ Log viewing complete${NC}"
echo ""
echo "Useful commands:"
echo "  - Follow logs: $0 -f $COMPONENT"
echo "  - More lines: $0 -n 500 $COMPONENT"
echo "  - Previous container: $0 -p $COMPONENT"
echo "  - All components: $0 all"
