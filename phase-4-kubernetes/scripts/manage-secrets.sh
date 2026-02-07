#!/bin/bash

# Phase IV - Secret Management Helper Script (Linux/macOS)
# Simplifies secret creation, viewing, updating, and deletion

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

NAMESPACE="todo-app"
SECRET_NAME="todo-app-secrets"

# Function to display usage
usage() {
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  create    - Create new secrets (interactive)"
    echo "  update    - Update existing secrets (interactive)"
    echo "  view      - View current secrets (decoded)"
    echo "  delete    - Delete secrets"
    echo "  backup    - Backup secrets to file"
    echo "  restore   - Restore secrets from backup file"
    echo "  rotate    - Rotate specific secret"
    echo ""
    echo "Examples:"
    echo "  $0 create                    # Create new secrets"
    echo "  $0 update                    # Update existing secrets"
    echo "  $0 view                      # View current secrets"
    echo "  $0 backup secrets.backup     # Backup to file"
    echo "  $0 restore secrets.backup    # Restore from file"
    echo "  $0 rotate SECRET_KEY         # Rotate specific secret"
    echo ""
    exit 1
}

# Check if command provided
if [ $# -eq 0 ]; then
    usage
fi

COMMAND=$1

# Function to check if namespace exists
check_namespace() {
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        echo -e "${RED}Error: Namespace '$NAMESPACE' not found${NC}"
        echo "Please deploy the application first"
        exit 1
    fi
}

# Function to check if secret exists
secret_exists() {
    kubectl get secret $SECRET_NAME -n $NAMESPACE &> /dev/null
}

# Function to prompt for secret value
prompt_secret() {
    local key=$1
    local description=$2
    local current_value=$3

    echo ""
    echo -e "${BLUE}$key${NC}"
    echo "  Description: $description"

    if [ -n "$current_value" ]; then
        echo "  Current value: ${current_value:0:10}... (hidden)"
        echo -n "  New value (press Enter to keep current): "
    else
        echo -n "  Value: "
    fi

    read -s value
    echo ""

    if [ -z "$value" ] && [ -n "$current_value" ]; then
        echo "$current_value"
    else
        echo "$value"
    fi
}

# Function to generate random secret key
generate_secret_key() {
    openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))"
}

# Command: create
cmd_create() {
    check_namespace

    if secret_exists; then
        echo -e "${YELLOW}Warning: Secret '$SECRET_NAME' already exists${NC}"
        echo -n "Do you want to replace it? (y/N): "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "Aborted"
            exit 0
        fi
    fi

    echo "========================================="
    echo "Create Secrets - Todo App"
    echo "========================================="
    echo ""
    echo "This will create secrets for the Todo App."
    echo "Press Ctrl+C to cancel at any time."
    echo ""

    # Prompt for each secret
    DATABASE_URL=$(prompt_secret "DATABASE_URL" \
        "PostgreSQL connection string" \
        "")

    if [ -z "$DATABASE_URL" ]; then
        DATABASE_URL="postgresql://postgres:password@database:5432/todo_db"
        echo -e "${YELLOW}Using default: $DATABASE_URL${NC}"
    fi

    SECRET_KEY=$(prompt_secret "SECRET_KEY" \
        "Application secret key for JWT/sessions" \
        "")

    if [ -z "$SECRET_KEY" ]; then
        SECRET_KEY=$(generate_secret_key)
        echo -e "${YELLOW}Generated random secret key${NC}"
    fi

    OPENAI_API_KEY=$(prompt_secret "OPENAI_API_KEY" \
        "OpenAI API key for chatbot (optional)" \
        "")

    # Create secret
    echo ""
    echo "Creating secret..."

    kubectl create secret generic $SECRET_NAME \
        -n $NAMESPACE \
        --from-literal=DATABASE_URL="$DATABASE_URL" \
        --from-literal=SECRET_KEY="$SECRET_KEY" \
        --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
        --dry-run=client -o yaml | kubectl apply -f -

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Secret created successfully${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Restart pods to pick up new secrets:"
        echo "     kubectl rollout restart deployment/backend -n $NAMESPACE"
        echo "  2. Verify application functionality"
    else
        echo -e "${RED}✗ Failed to create secret${NC}"
        exit 1
    fi
}

# Command: update
cmd_update() {
    check_namespace

    if ! secret_exists; then
        echo -e "${RED}Error: Secret '$SECRET_NAME' not found${NC}"
        echo "Use '$0 create' to create secrets first"
        exit 1
    fi

    echo "========================================="
    echo "Update Secrets - Todo App"
    echo "========================================="
    echo ""
    echo "This will update existing secrets."
    echo "Press Enter to keep current value."
    echo "Press Ctrl+C to cancel at any time."
    echo ""

    # Get current values
    CURRENT_DATABASE_URL=$(kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.DATABASE_URL}' 2>/dev/null | base64 --decode)
    CURRENT_SECRET_KEY=$(kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.SECRET_KEY}' 2>/dev/null | base64 --decode)
    CURRENT_OPENAI_API_KEY=$(kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.OPENAI_API_KEY}' 2>/dev/null | base64 --decode)

    # Prompt for each secret
    DATABASE_URL=$(prompt_secret "DATABASE_URL" \
        "PostgreSQL connection string" \
        "$CURRENT_DATABASE_URL")

    SECRET_KEY=$(prompt_secret "SECRET_KEY" \
        "Application secret key for JWT/sessions" \
        "$CURRENT_SECRET_KEY")

    OPENAI_API_KEY=$(prompt_secret "OPENAI_API_KEY" \
        "OpenAI API key for chatbot (optional)" \
        "$CURRENT_OPENAI_API_KEY")

    # Update secret
    echo ""
    echo "Updating secret..."

    kubectl create secret generic $SECRET_NAME \
        -n $NAMESPACE \
        --from-literal=DATABASE_URL="$DATABASE_URL" \
        --from-literal=SECRET_KEY="$SECRET_KEY" \
        --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
        --dry-run=client -o yaml | kubectl apply -f -

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Secret updated successfully${NC}"
        echo ""
        echo "⚠️  IMPORTANT: Restart pods to pick up changes:"
        echo "   kubectl rollout restart deployment/backend -n $NAMESPACE"
        echo "   kubectl rollout restart deployment/frontend -n $NAMESPACE"
    else
        echo -e "${RED}✗ Failed to update secret${NC}"
        exit 1
    fi
}

# Command: view
cmd_view() {
    check_namespace

    if ! secret_exists; then
        echo -e "${RED}Error: Secret '$SECRET_NAME' not found${NC}"
        exit 1
    fi

    echo "========================================="
    echo "View Secrets - Todo App"
    echo "========================================="
    echo ""

    echo -e "${BLUE}DATABASE_URL:${NC}"
    kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.DATABASE_URL}' 2>/dev/null | base64 --decode
    echo ""
    echo ""

    echo -e "${BLUE}SECRET_KEY:${NC}"
    kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.SECRET_KEY}' 2>/dev/null | base64 --decode
    echo ""
    echo ""

    echo -e "${BLUE}OPENAI_API_KEY:${NC}"
    OPENAI_KEY=$(kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.OPENAI_API_KEY}' 2>/dev/null | base64 --decode)
    if [ -n "$OPENAI_KEY" ]; then
        echo "$OPENAI_KEY"
    else
        echo "(not set)"
    fi
    echo ""

    echo ""
    echo -e "${YELLOW}⚠️  WARNING: These are sensitive values. Do not share!${NC}"
}

# Command: delete
cmd_delete() {
    check_namespace

    if ! secret_exists; then
        echo -e "${YELLOW}Secret '$SECRET_NAME' not found${NC}"
        exit 0
    fi

    echo -e "${YELLOW}Warning: This will delete all secrets for the Todo App${NC}"
    echo -n "Are you sure? (y/N): "
    read -r response

    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 0
    fi

    kubectl delete secret $SECRET_NAME -n $NAMESPACE

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Secret deleted successfully${NC}"
    else
        echo -e "${RED}✗ Failed to delete secret${NC}"
        exit 1
    fi
}

# Command: backup
cmd_backup() {
    check_namespace

    if ! secret_exists; then
        echo -e "${RED}Error: Secret '$SECRET_NAME' not found${NC}"
        exit 1
    fi

    BACKUP_FILE=${2:-"secrets-backup-$(date +%Y%m%d-%H%M%S).yaml"}

    echo "Backing up secrets to: $BACKUP_FILE"

    kubectl get secret $SECRET_NAME -n $NAMESPACE -o yaml > "$BACKUP_FILE"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Secrets backed up successfully${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  WARNING: This file contains sensitive data!${NC}"
        echo "   - Store it securely"
        echo "   - Do not commit to version control"
        echo "   - Delete after use"
    else
        echo -e "${RED}✗ Failed to backup secrets${NC}"
        exit 1
    fi
}

# Command: restore
cmd_restore() {
    check_namespace

    BACKUP_FILE=$2

    if [ -z "$BACKUP_FILE" ]; then
        echo -e "${RED}Error: Backup file not specified${NC}"
        echo "Usage: $0 restore <backup-file>"
        exit 1
    fi

    if [ ! -f "$BACKUP_FILE" ]; then
        echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
        exit 1
    fi

    echo "Restoring secrets from: $BACKUP_FILE"

    if secret_exists; then
        echo -e "${YELLOW}Warning: This will replace existing secrets${NC}"
        echo -n "Continue? (y/N): "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "Aborted"
            exit 0
        fi
    fi

    kubectl apply -f "$BACKUP_FILE"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Secrets restored successfully${NC}"
        echo ""
        echo "Restart pods to pick up restored secrets:"
        echo "  kubectl rollout restart deployment/backend -n $NAMESPACE"
    else
        echo -e "${RED}✗ Failed to restore secrets${NC}"
        exit 1
    fi
}

# Command: rotate
cmd_rotate() {
    check_namespace

    if ! secret_exists; then
        echo -e "${RED}Error: Secret '$SECRET_NAME' not found${NC}"
        exit 1
    fi

    KEY_NAME=$2

    if [ -z "$KEY_NAME" ]; then
        echo -e "${RED}Error: Secret key not specified${NC}"
        echo "Usage: $0 rotate <key-name>"
        echo ""
        echo "Available keys:"
        echo "  - DATABASE_URL"
        echo "  - SECRET_KEY"
        echo "  - OPENAI_API_KEY"
        exit 1
    fi

    echo "========================================="
    echo "Rotate Secret - $KEY_NAME"
    echo "========================================="
    echo ""

    # Get current values
    CURRENT_DATABASE_URL=$(kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.DATABASE_URL}' 2>/dev/null | base64 --decode)
    CURRENT_SECRET_KEY=$(kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.SECRET_KEY}' 2>/dev/null | base64 --decode)
    CURRENT_OPENAI_API_KEY=$(kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.OPENAI_API_KEY}' 2>/dev/null | base64 --decode)

    case $KEY_NAME in
        DATABASE_URL)
            NEW_VALUE=$(prompt_secret "DATABASE_URL" "New PostgreSQL connection string" "")
            DATABASE_URL=$NEW_VALUE
            SECRET_KEY=$CURRENT_SECRET_KEY
            OPENAI_API_KEY=$CURRENT_OPENAI_API_KEY
            ;;
        SECRET_KEY)
            echo "Generating new secret key..."
            NEW_VALUE=$(generate_secret_key)
            echo -e "${GREEN}Generated: ${NEW_VALUE:0:20}...${NC}"
            DATABASE_URL=$CURRENT_DATABASE_URL
            SECRET_KEY=$NEW_VALUE
            OPENAI_API_KEY=$CURRENT_OPENAI_API_KEY
            ;;
        OPENAI_API_KEY)
            NEW_VALUE=$(prompt_secret "OPENAI_API_KEY" "New OpenAI API key" "")
            DATABASE_URL=$CURRENT_DATABASE_URL
            SECRET_KEY=$CURRENT_SECRET_KEY
            OPENAI_API_KEY=$NEW_VALUE
            ;;
        *)
            echo -e "${RED}Error: Unknown secret key: $KEY_NAME${NC}"
            exit 1
            ;;
    esac

    # Update secret
    echo ""
    echo "Rotating secret..."

    kubectl create secret generic $SECRET_NAME \
        -n $NAMESPACE \
        --from-literal=DATABASE_URL="$DATABASE_URL" \
        --from-literal=SECRET_KEY="$SECRET_KEY" \
        --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
        --dry-run=client -o yaml | kubectl apply -f -

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Secret rotated successfully${NC}"
        echo ""
        echo "⚠️  IMPORTANT: Restart pods to pick up changes:"
        echo "   kubectl rollout restart deployment/backend -n $NAMESPACE"

        if [ "$KEY_NAME" = "SECRET_KEY" ]; then
            echo ""
            echo -e "${YELLOW}⚠️  NOTE: Rotating SECRET_KEY will invalidate existing sessions${NC}"
        fi
    else
        echo -e "${RED}✗ Failed to rotate secret${NC}"
        exit 1
    fi
}

# Execute command
case $COMMAND in
    create)
        cmd_create
        ;;
    update)
        cmd_update
        ;;
    view)
        cmd_view
        ;;
    delete)
        cmd_delete
        ;;
    backup)
        cmd_backup "$@"
        ;;
    restore)
        cmd_restore "$@"
        ;;
    rotate)
        cmd_rotate "$@"
        ;;
    *)
        echo -e "${RED}Error: Unknown command: $COMMAND${NC}"
        usage
        ;;
esac
