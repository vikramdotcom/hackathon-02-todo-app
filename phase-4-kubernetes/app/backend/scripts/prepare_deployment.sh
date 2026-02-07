#!/bin/bash
# Pre-deployment cleanup script for Hugging Face Spaces
# Ensures clean state before deployment

set -e  # Exit on error

echo "🚀 Preparing backend for Hugging Face deployment..."
echo ""

# Navigate to backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

echo "📂 Working directory: $BACKEND_DIR"
echo ""

# Step 1: Remove old database files
echo "🗑️  Step 1: Removing old database files..."
if ls *.db 1> /dev/null 2>&1; then
    rm -f *.db
    echo "   ✅ Removed old database files"
else
    echo "   ℹ️  No database files found (good!)"
fi
echo ""

# Step 2: Verify .gitignore
echo "📝 Step 2: Checking .gitignore..."
if [ -f .gitignore ]; then
    if grep -q "^\*.db$" .gitignore; then
        echo "   ✅ .gitignore already contains *.db"
    else
        echo "*.db" >> .gitignore
        echo "   ✅ Added *.db to .gitignore"
    fi
else
    echo "*.db" > .gitignore
    echo "   ✅ Created .gitignore with *.db"
fi
echo ""

# Step 3: Verify migration file
echo "🔍 Step 3: Verifying migration file..."
if grep -q "~\*\|ALTER TABLE.*ADD CONSTRAINT" alembic/versions/*.py 2>/dev/null; then
    echo "   ❌ ERROR: Found PostgreSQL-specific operators in migration!"
    echo "   Please fix the migration file before deploying."
    exit 1
else
    echo "   ✅ Migration file is SQLite-compatible"
fi
echo ""

# Step 4: Check required files
echo "📦 Step 4: Checking required files..."
REQUIRED_FILES=(
    "app/main.py"
    "app/core/startup.py"
    "alembic/env.py"
    "alembic/versions/001_initial_schema.py"
    "requirements.txt"
)

ALL_PRESENT=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ Missing: $file"
        ALL_PRESENT=false
    fi
done

if [ "$ALL_PRESENT" = false ]; then
    echo ""
    echo "   ❌ Some required files are missing!"
    exit 1
fi
echo ""

# Step 5: Test migrations locally (optional)
echo "🧪 Step 5: Testing migrations locally..."
read -p "   Run migration test? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   Running migration test..."
    python scripts/reset_db.py
    if [ $? -eq 0 ]; then
        echo "   ✅ Migration test passed"
        # Clean up test database
        rm -f todo_app.db
        echo "   🗑️  Cleaned up test database"
    else
        echo "   ❌ Migration test failed!"
        exit 1
    fi
else
    echo "   ⏭️  Skipped migration test"
fi
echo ""

# Step 6: Check git status
echo "📊 Step 6: Checking git status..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    if git status --porcelain | grep -q "\.db$"; then
        echo "   ⚠️  WARNING: Database files are staged for commit!"
        echo "   Run: git reset HEAD *.db"
    else
        echo "   ✅ No database files in git staging"
    fi
else
    echo "   ℹ️  Not a git repository"
fi
echo ""

# Summary
echo "✅ Pre-deployment checks complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: git status"
echo "   2. Commit changes: git add . && git commit -m 'fix: SQLite migration for HF deployment'"
echo "   3. Push to repository: git push"
echo "   4. Deploy to Hugging Face Spaces"
echo ""
echo "📚 See HUGGINGFACE_DEPLOYMENT.md for detailed deployment instructions"
echo ""
