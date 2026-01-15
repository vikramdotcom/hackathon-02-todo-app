# Hugging Face Spaces Deployment Guide

## ✅ SQLite Migration Fix - PERMANENT SOLUTION

This guide ensures your Todo App backend deploys successfully on Hugging Face Spaces with zero migration errors.

---

## 🔧 What Was Fixed

### Problem
The original migration used PostgreSQL-specific regex operators (`~*`) and `ALTER TABLE ADD CONSTRAINT`, which SQLite doesn't support:
```sql
ALTER TABLE users ADD CONSTRAINT chk_email_format CHECK (email ~* regex)
```

### Solution Implemented
1. **✅ Migration Fixed** (`alembic/versions/001_initial_schema.py`)
   - All constraints defined inline during `CREATE TABLE`
   - No `ALTER TABLE ADD CONSTRAINT` statements
   - No PostgreSQL-specific operators
   - SQLite-compatible CHECK constraints only

2. **✅ Email Validation in Python** (`app/models/user.py`)
   - Pydantic `@field_validator` for email format validation
   - Regex validation at application layer (not database)
   - Works across all database backends

3. **✅ Batch Mode Enabled** (`alembic/env.py`)
   - `render_as_batch=True` for SQLite compatibility
   - Automatic detection of SQLite dialect
   - Safe for both online and offline migrations

4. **✅ Automatic Database Recovery** (`app/core/startup.py`)
   - Health checks on startup
   - Automatic reset if corrupted database detected
   - Fresh migrations applied automatically
   - Safe for Hugging Face Spaces deployment

5. **✅ Startup Integration** (`app/main.py`)
   - FastAPI lifespan events
   - Database initialization on app startup
   - Error handling and logging

---

## 🚀 Pre-Deployment Checklist

### Step 1: Clean Old Database (CRITICAL)
```bash
# Navigate to backend directory
cd phase-2-web-app/backend

# Remove old corrupted database
rm -f todo_app.db
rm -f *.db

# Verify removal
ls -la *.db  # Should show "No such file or directory"
```

### Step 2: Test Migrations Locally
```bash
# Reset and test migrations
python scripts/reset_db.py

# Verify database was created successfully
ls -la todo_app.db  # Should exist

# Test the application
uvicorn app.main:app --reload

# Check health endpoint
curl http://localhost:8000/health
```

### Step 3: Verify Migration File
```bash
# Check migration has no PostgreSQL operators
grep -n "~\*\|ALTER TABLE.*ADD CONSTRAINT" alembic/versions/*.py

# Should return nothing (no matches)
```

### Step 4: Commit Clean State
```bash
# Remove database file before committing
rm -f todo_app.db
rm -f *.db

# Add .gitignore entry if not present
echo "*.db" >> .gitignore

# Commit changes
git add .
git commit -m "fix: permanent SQLite migration fix for Hugging Face deployment"
git push
```

---

## 📦 Hugging Face Spaces Configuration

### Required Files

1. **`requirements.txt`** - Ensure these dependencies:
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlmodel>=0.0.14
alembic>=1.12.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
pydantic[email]>=2.0.0
pydantic-settings>=2.0.0
```

2. **`Dockerfile`** or **`app.py`** (Hugging Face entry point)

Example `app.py` for Hugging Face:
```python
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,  # Hugging Face Spaces default port
        log_level="info"
    )
```

3. **Environment Variables** (Set in Hugging Face Spaces settings)
```bash
DATABASE_URL=sqlite:///./todo_app.db
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
```

---

## 🎯 Deployment Steps on Hugging Face

### Option A: Direct Git Push
1. Create new Space on Hugging Face
2. Select "Docker" or "Gradio" SDK
3. Connect your GitHub repository
4. Set environment variables in Space settings
5. Push your code - automatic deployment

### Option B: Manual Upload
1. Create new Space
2. Upload backend directory
3. Configure environment variables
4. Deploy

---

## ✅ Post-Deployment Verification

### 1. Check Application Logs
Look for these success messages:
```
INFO: Starting application...
INFO: Starting database initialization...
INFO: Database is healthy, no reset needed
INFO: Database initialization complete
INFO: Application startup complete
```

### 2. Test API Endpoints
```bash
# Replace with your Hugging Face Space URL
export HF_URL="https://your-space.hf.space"

# Health check
curl $HF_URL/health

# API docs
curl $HF_URL/docs

# Root endpoint
curl $HF_URL/
```

### 3. Test User Registration
```bash
curl -X POST "$HF_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

---

## 🔍 Troubleshooting

### Issue: "near 'CONSTRAINT': syntax error"
**Solution:** Old database file exists. Remove it:
```bash
rm -f todo_app.db *.db
git push  # Redeploy
```

### Issue: "No such table: users"
**Solution:** Migrations didn't run. Check logs for:
- Alembic configuration errors
- Database URL issues
- File permission problems

### Issue: "Email validation not working"
**Solution:** Email validation is now in Python layer (`app/models/user.py:20-30`). Check:
- Pydantic validators are working
- Email format matches regex pattern

### Issue: Database resets on every deployment
**Solution:** This is expected behavior if database is corrupted. To persist data:
1. Use persistent storage (Hugging Face Spaces persistent storage)
2. Or use external database (PostgreSQL, MySQL)

---

## 🎉 Success Indicators

✅ No migration errors in logs
✅ Health endpoint returns `{"status": "healthy"}`
✅ API docs accessible at `/docs`
✅ User registration works
✅ Email validation works (Python layer)
✅ Database persists between requests (within same session)

---

## 📚 Technical Details

### Migration Strategy
- **Inline Constraints:** All CHECK constraints defined during CREATE TABLE
- **No ALTER TABLE:** SQLite doesn't support adding constraints after table creation
- **Batch Mode:** Alembic batch mode for SQLite compatibility
- **Python Validation:** Email/username validation at application layer

### Database Recovery Flow
1. App starts → `lifespan` event triggered
2. `initialize_database()` called
3. `check_database_health()` verifies tables and structure
4. If unhealthy → remove corrupted DB → run fresh migrations
5. If healthy → continue normally

### Why This Works
- **No PostgreSQL Dependencies:** Pure SQLite-compatible SQL
- **Application-Layer Validation:** Pydantic validators catch invalid data
- **Automatic Recovery:** Corrupted databases auto-reset on startup
- **Production-Ready:** Proper error handling and logging

---

## 🔐 Security Notes

1. **Never commit database files:** Add `*.db` to `.gitignore`
2. **Use strong SECRET_KEY:** Generate with `openssl rand -hex 32`
3. **Enable HTTPS:** Hugging Face Spaces provides this automatically
4. **Validate all inputs:** Pydantic models handle this

---

## 📞 Support

If you encounter issues:
1. Check application logs in Hugging Face Spaces
2. Verify all environment variables are set
3. Ensure no `.db` files in repository
4. Test migrations locally first

---

**Last Updated:** 2026-01-16
**Status:** ✅ Production-Ready
**Tested On:** Hugging Face Spaces (SQLite)
