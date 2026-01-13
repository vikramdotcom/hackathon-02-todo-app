# Phase II Quickstart Guide

**Feature**: Phase II – Full-Stack Web Application
**Date**: 2026-01-10
**Audience**: Developers setting up Phase II for the first time

## Overview

This guide provides step-by-step instructions for setting up and running the Phase II full-stack web application locally. Follow these instructions to get the backend API and frontend UI running on your development machine.

## Prerequisites

Before starting, ensure you have the following installed:

### Required Software

- **Node.js**: Version 18.0.0 or higher
  - Check: `node --version`
  - Download: https://nodejs.org/

- **Python**: Version 3.13.0 or higher
  - Check: `python --version` or `python3 --version`
  - Download: https://www.python.org/

- **Git**: Latest version
  - Check: `git --version`
  - Download: https://git-scm.com/

### Required Accounts

- **Neon DB Account**: Free tier is sufficient
  - Sign up: https://neon.tech/
  - Create a new project and database
  - Copy the connection string (starts with `postgresql://`)

### Optional Tools

- **Postman** or **Insomnia**: For API testing
- **PostgreSQL Client**: For database inspection (pgAdmin, DBeaver, etc.)

---

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd hackathon-02-todo-app
git checkout 002-phase-2-web-app
```

### Step 2: Backend Setup

#### 2.1 Navigate to Backend Directory

```bash
cd phase-2-web-app/backend
```

#### 2.2 Create Python Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

#### 2.3 Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- FastAPI
- SQLModel
- Pydantic
- python-jose (JWT)
- passlib (password hashing)
- psycopg2 (PostgreSQL driver)
- uvicorn (ASGI server)
- alembic (database migrations)

#### 2.4 Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# JWT Configuration
SECRET_KEY=your-secret-key-here-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=Todo App Phase II

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

**Generate a secure SECRET_KEY:**
```bash
openssl rand -hex 32
```

**Get your DATABASE_URL from Neon DB:**
1. Log in to Neon console
2. Select your project
3. Go to "Connection Details"
4. Copy the connection string
5. Paste into `.env` file

#### 2.5 Run Database Migrations

```bash
alembic upgrade head
```

This creates the `users` and `todos` tables with all indexes and constraints.

#### 2.6 Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend is Running:**
- Open browser: http://localhost:8000/docs
- You should see the FastAPI Swagger documentation

---

### Step 3: Frontend Setup

Open a **new terminal window** (keep backend running).

#### 3.1 Navigate to Frontend Directory

```bash
cd phase-2-web-app/frontend
```

#### 3.2 Install Node Dependencies

```bash
npm install
```

This installs:
- Next.js 14
- React 18
- Tailwind CSS
- Axios
- TypeScript
- And all other dependencies

#### 3.3 Configure Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

#### 3.4 Start Frontend Development Server

```bash
npm run dev
```

**Expected Output:**
```
   ▲ Next.js 14.0.0
   - Local:        http://localhost:3000
   - Network:      http://192.168.1.x:3000

 ✓ Ready in 2.5s
```

**Verify Frontend is Running:**
- Open browser: http://localhost:3000
- You should see the landing page

---

## First-Time Usage

### Step 4: Create Your First User

#### 4.1 Register a New Account

1. Navigate to http://localhost:3000/register
2. Fill in the registration form:
   - Email: your-email@example.com
   - Username: yourusername
   - Password: SecurePass123
3. Click "Register"
4. You'll be redirected to the login page

#### 4.2 Log In

1. Navigate to http://localhost:3000/login (or you're already there)
2. Enter your credentials:
   - Email: your-email@example.com
   - Password: SecurePass123
3. Click "Login"
4. You'll be redirected to your dashboard

#### 4.3 Create Your First Todo

1. On the dashboard, click "Add Todo"
2. Fill in the form:
   - Title: "Complete Phase II setup"
   - Description: "Successfully set up and run Phase II locally"
   - Priority: High
   - Tags: setup, phase-2
   - Due Date: (optional)
3. Click "Create"
4. Your todo appears in the list!

---

## Testing the API

### Using Swagger UI (Recommended for Beginners)

1. Navigate to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"
6. See the response below

### Using cURL

**Register a user:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

Save the `access_token` from the response.

**Create a todo:**
```bash
curl -X POST http://localhost:8000/api/v1/todos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{
    "title": "Test todo from cURL",
    "priority": "high"
  }'
```

**Get all todos:**
```bash
curl -X GET http://localhost:8000/api/v1/todos \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## Running Tests

### Backend Tests

```bash
cd phase-2-web-app/backend
pytest
```

**Run specific test types:**
```bash
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/          # End-to-end tests only
```

**Run with coverage:**
```bash
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd phase-2-web-app/frontend
npm test              # Run all tests
npm run test:watch    # Run tests in watch mode
npm run test:coverage # Run with coverage report
```

**Run E2E tests:**
```bash
npm run test:e2e
```

---

## Common Issues and Solutions

### Issue: "Module not found" errors in backend

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Database connection fails

**Solution:**
1. Verify DATABASE_URL in `.env` is correct
2. Check Neon DB console - is the database running?
3. Ensure connection string includes `?sslmode=require`
4. Test connection:
   ```bash
   psql "postgresql://user:password@host/database?sslmode=require"
   ```

### Issue: Frontend can't connect to backend

**Solution:**
1. Verify backend is running on port 8000
2. Check NEXT_PUBLIC_API_URL in `.env.local`
3. Check browser console for CORS errors
4. Verify BACKEND_CORS_ORIGINS in backend `.env` includes frontend URL

### Issue: "Port already in use"

**Backend (port 8000):**
```bash
# Find process using port 8000
lsof -i :8000          # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>          # macOS/Linux
taskkill /PID <PID> /F # Windows
```

**Frontend (port 3000):**
```bash
# Find and kill process using port 3000
lsof -i :3000          # macOS/Linux
netstat -ano | findstr :3000  # Windows
```

### Issue: JWT token expired

**Solution:**
- Log out and log back in
- Token expires after 24 hours (configurable in backend `.env`)

### Issue: Alembic migration fails

**Solution:**
```bash
# Reset database (WARNING: deletes all data)
alembic downgrade base
alembic upgrade head

# Or create a new database in Neon and update DATABASE_URL
```

---

## Development Workflow

### Making Changes

**Backend Changes:**
1. Edit code in `backend/app/`
2. Server auto-reloads (uvicorn --reload)
3. Test changes in Swagger UI or frontend
4. Run tests: `pytest`

**Frontend Changes:**
1. Edit code in `frontend/src/`
2. Next.js auto-reloads
3. See changes immediately in browser
4. Run tests: `npm test`

### Database Schema Changes

1. Edit SQLModel models in `backend/app/models/`
2. Generate migration:
   ```bash
   alembic revision --autogenerate -m "Description of change"
   ```
3. Review generated migration in `backend/alembic/versions/`
4. Apply migration:
   ```bash
   alembic upgrade head
   ```

### Adding New API Endpoints

1. Define route in `backend/app/api/routes/`
2. Add business logic in `backend/app/services/`
3. Update schemas in `backend/app/schemas/` if needed
4. Test in Swagger UI
5. Write tests in `backend/tests/`

### Adding New Frontend Components

1. Create component in `frontend/src/components/`
2. Import and use in pages
3. Add styles with Tailwind CSS
4. Write tests in `frontend/tests/`

---

## Next Steps

After successfully running Phase II locally:

1. **Explore the API**: Try all endpoints in Swagger UI
2. **Test the UI**: Create, update, delete todos through the web interface
3. **Run Tests**: Ensure all tests pass
4. **Read the Code**: Understand the architecture and patterns
5. **Make Changes**: Try adding a new feature or fixing a bug
6. **Prepare for Phase III**: Review AI agent integration requirements

---

## Additional Resources

### Documentation

- **Specification**: `specs/002-phase-2-web-app/spec.md`
- **Implementation Plan**: `specs/002-phase-2-web-app/plan.md`
- **Data Model**: `specs/002-phase-2-web-app/data-model.md`
- **API Contracts**: `specs/002-phase-2-web-app/contracts/api-endpoints.md`
- **Database Schema**: `specs/002-phase-2-web-app/contracts/database-schema.md`

### Technology Documentation

- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs
- **SQLModel**: https://sqlmodel.tiangolo.com/
- **Neon DB**: https://neon.tech/docs
- **Tailwind CSS**: https://tailwindcss.com/docs

### Getting Help

- Check the specification for requirements
- Review the implementation plan for architecture decisions
- Read the research document for technology choices
- Check GitHub issues for known problems
- Ask questions in team chat or create an issue

---

## Summary

You should now have:
- ✅ Backend API running on http://localhost:8000
- ✅ Frontend UI running on http://localhost:3000
- ✅ Database connected and migrated
- ✅ First user account created
- ✅ First todo created

**Congratulations!** You've successfully set up Phase II. You're ready to start development or testing.

---

**Last Updated**: 2026-01-10
**Status**: ✅ Complete and tested
