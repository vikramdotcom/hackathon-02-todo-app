# 🚀 Quick Start Guide - Phase II Todo App

## What We've Done So Far

✅ Backend dependencies installed (FastAPI, SQLModel, etc.)
✅ Frontend dependencies installing (Next.js, React, etc.)
✅ Environment files created
✅ Generated SECRET_KEY: `1ad902292471f4356ee6d951a6cba1a3eea8fcadb89118d86fbbbd3cb8eec3a2`

## What You Need to Do

### Step 1: Set Up Neon Database (5 minutes)

1. Go to https://neon.tech/ and sign up (free)
2. Click "Create Project"
3. Give it a name (e.g., "todo-app")
4. Click "Create Project"
5. Copy the connection string - it looks like:
   ```
   postgresql://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### Step 2: Update Backend Environment File

Open `phase-2-web-app/backend/.env` and update these two lines:

```env
# Replace this line with your Neon DB connection string:
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Replace this line with the generated secret key:
SECRET_KEY=1ad902292471f4356ee6d951a6cba1a3eea8fcadb89118d86fbbbd3cb8eec3a2
```

### Step 3: Run Database Migrations

Open a terminal and run:

```bash
cd phase-2-web-app/backend
venv/Scripts/activate  # On Windows
# source venv/bin/activate  # On Mac/Linux

alembic upgrade head
```

This creates the `users` and `todos` tables in your database.

### Step 4: Start the Backend Server

In the same terminal (with venv activated):

```bash
venv/Scripts/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

**Test it**: Open http://localhost:8000/docs in your browser - you should see the API documentation!

### Step 5: Start the Frontend Server

Open a **NEW terminal** (keep backend running) and run:

```bash
cd phase-2-web-app/frontend
npm run dev
```

You should see:
```
▲ Next.js 14.0.0
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000

✓ Ready in 2.5s
```

**Test it**: Open http://localhost:3000 in your browser - you should see the landing page!

### Step 6: Use the Application

1. Click "Get Started" to register
2. Fill in:
   - Email: your-email@example.com
   - Username: yourusername
   - Password: password123
3. Click "Create Account"
4. Log in with your credentials
5. Create your first todo!

## Troubleshooting

### Backend won't start?
- Check that DATABASE_URL in `.env` is correct
- Make sure you ran `alembic upgrade head`
- Check that port 8000 is not in use

### Frontend won't start?
- Make sure `npm install` finished successfully
- Check that NEXT_PUBLIC_API_URL in `.env.local` is `http://localhost:8000/api/v1`
- Check that port 3000 is not in use

### Can't connect to database?
- Verify your Neon DB connection string is correct
- Make sure it includes `?sslmode=require` at the end
- Check that your Neon project is active

## Quick Commands Reference

**Backend**:
```bash
cd phase-2-web-app/backend
venv/Scripts/activate
venv/Scripts/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**:
```bash
cd phase-2-web-app/frontend
npm run dev
```

**Database Migrations**:
```bash
cd phase-2-web-app/backend
venv/Scripts/activate
alembic upgrade head
```

## What's Next?

Once both servers are running:
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

Enjoy your full-stack todo application! 🎉
