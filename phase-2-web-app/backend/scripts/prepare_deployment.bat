@echo off
REM Pre-deployment cleanup script for Hugging Face Spaces (Windows)
REM Ensures clean state before deployment

echo.
echo 🚀 Preparing backend for Hugging Face deployment...
echo.

cd /d "%~dp0\.."
echo 📂 Working directory: %CD%
echo.

REM Step 1: Remove old database files
echo 🗑️  Step 1: Removing old database files...
if exist *.db (
    del /Q *.db
    echo    ✅ Removed old database files
) else (
    echo    ℹ️  No database files found (good!)
)
echo.

REM Step 2: Verify .gitignore
echo 📝 Step 2: Checking .gitignore...
if exist .gitignore (
    findstr /C:"*.db" .gitignore >nul
    if errorlevel 1 (
        echo *.db >> .gitignore
        echo    ✅ Added *.db to .gitignore
    ) else (
        echo    ✅ .gitignore already contains *.db
    )
) else (
    echo *.db > .gitignore
    echo    ✅ Created .gitignore with *.db
)
echo.

REM Step 3: Verify migration file
echo 🔍 Step 3: Verifying migration file...
findstr /C:"~*" /C:"ALTER TABLE.*ADD CONSTRAINT" alembic\versions\*.py >nul 2>&1
if not errorlevel 1 (
    echo    ❌ ERROR: Found PostgreSQL-specific operators in migration!
    echo    Please fix the migration file before deploying.
    exit /b 1
) else (
    echo    ✅ Migration file is SQLite-compatible
)
echo.

REM Step 4: Check required files
echo 📦 Step 4: Checking required files...
set ALL_PRESENT=1

if exist app\main.py (echo    ✅ app\main.py) else (echo    ❌ Missing: app\main.py & set ALL_PRESENT=0)
if exist app\core\startup.py (echo    ✅ app\core\startup.py) else (echo    ❌ Missing: app\core\startup.py & set ALL_PRESENT=0)
if exist alembic\env.py (echo    ✅ alembic\env.py) else (echo    ❌ Missing: alembic\env.py & set ALL_PRESENT=0)
if exist alembic\versions\001_initial_schema.py (echo    ✅ alembic\versions\001_initial_schema.py) else (echo    ❌ Missing: alembic\versions\001_initial_schema.py & set ALL_PRESENT=0)
if exist requirements.txt (echo    ✅ requirements.txt) else (echo    ❌ Missing: requirements.txt & set ALL_PRESENT=0)

if %ALL_PRESENT%==0 (
    echo.
    echo    ❌ Some required files are missing!
    exit /b 1
)
echo.

REM Step 5: Test migrations locally (optional)
echo 🧪 Step 5: Testing migrations locally...
set /p REPLY="   Run migration test? (y/N): "
if /i "%REPLY%"=="y" (
    echo    Running migration test...
    python scripts\reset_db.py
    if errorlevel 1 (
        echo    ❌ Migration test failed!
        exit /b 1
    ) else (
        echo    ✅ Migration test passed
        if exist todo_app.db (
            del /Q todo_app.db
            echo    🗑️  Cleaned up test database
        )
    )
) else (
    echo    ⏭️  Skipped migration test
)
echo.

REM Step 6: Check git status
echo 📊 Step 6: Checking git status...
git rev-parse --git-dir >nul 2>&1
if not errorlevel 1 (
    git status --porcelain | findstr /C:".db" >nul
    if not errorlevel 1 (
        echo    ⚠️  WARNING: Database files are staged for commit!
        echo    Run: git reset HEAD *.db
    ) else (
        echo    ✅ No database files in git staging
    )
) else (
    echo    ℹ️  Not a git repository
)
echo.

REM Summary
echo ✅ Pre-deployment checks complete!
echo.
echo 📋 Next steps:
echo    1. Review changes: git status
echo    2. Commit changes: git add . ^&^& git commit -m "fix: SQLite migration for HF deployment"
echo    3. Push to repository: git push
echo    4. Deploy to Hugging Face Spaces
echo.
echo 📚 See HUGGINGFACE_DEPLOYMENT.md for detailed deployment instructions
echo.
pause
