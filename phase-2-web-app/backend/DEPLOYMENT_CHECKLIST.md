# Hugging Face Spaces Deployment Checklist

Use this checklist to ensure your backend is ready for deployment to Hugging Face Spaces.

## Pre-Deployment Checklist

### ✅ Files Created
- [x] `Dockerfile` - Container configuration for HF Spaces
- [x] `README.md` - Space documentation with metadata
- [x] `.dockerignore` - Excludes unnecessary files from build
- [x] `DEPLOYMENT.md` - Detailed deployment guide
- [x] `.env.example` - Updated with SQLite configuration

### 📋 Configuration Review

- [ ] **Environment Variables Ready**
  - [ ] Generate SECRET_KEY: `openssl rand -hex 32`
  - [ ] Prepare DATABASE_URL: `sqlite:///./data/todo_app.db`
  - [ ] Set ENVIRONMENT: `production`
  - [ ] Configure CORS origins (if needed)

- [ ] **Code Review**
  - [ ] All dependencies in `requirements.txt`
  - [ ] No hardcoded secrets in code
  - [ ] Database migrations are up to date
  - [ ] Health check endpoint works (`/health`)

- [ ] **Testing Locally** (Optional but Recommended)
  - [ ] Test with SQLite locally
  - [ ] Run: `DATABASE_URL=sqlite:///./todo_app.db uvicorn app.main:app`
  - [ ] Verify all endpoints work
  - [ ] Test authentication flow

## Deployment Steps

### Step 1: Create Hugging Face Space
- [ ] Go to https://huggingface.co/spaces
- [ ] Click "Create new Space"
- [ ] Choose a name (e.g., `todo-app-api`)
- [ ] Select SDK: **Docker**
- [ ] Choose visibility (Public/Private)
- [ ] Click "Create Space"

### Step 2: Configure Secrets
- [ ] Go to Space Settings → Repository secrets
- [ ] Add `SECRET_KEY` (generated with openssl)
- [ ] Add `DATABASE_URL` = `sqlite:///./data/todo_app.db`
- [ ] Add `ENVIRONMENT` = `production`
- [ ] Add `BACKEND_CORS_ORIGINS` (if connecting to frontend)

### Step 3: Push Code

**Option A: Git Push**
```bash
cd phase-2-web-app/backend
git init
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
git add .
git commit -m "Initial deployment"
git push hf main
```

**Option B: Web Upload**
- [ ] Go to Space → Files tab
- [ ] Upload all backend files
- [ ] Ensure Dockerfile, README.md, and app/ are included

### Step 4: Monitor Build
- [ ] Watch build logs in Space dashboard
- [ ] Wait for "Running" status (3-5 minutes)
- [ ] Check for any error messages

### Step 5: Verify Deployment
- [ ] Test health endpoint: `https://YOUR_SPACE.hf.space/health`
- [ ] Access API docs: `https://YOUR_SPACE.hf.space/docs`
- [ ] Test user registration via `/api/v1/auth/register`
- [ ] Test login via `/api/v1/auth/login`
- [ ] Create a test todo via `/api/v1/todos`

## Post-Deployment Checklist

### Verification Tests
- [ ] **Health Check**
  ```bash
  curl https://YOUR_SPACE.hf.space/health
  # Expected: {"status": "healthy"}
  ```

- [ ] **API Documentation**
  - [ ] Visit `/docs` - Swagger UI loads
  - [ ] Visit `/redoc` - ReDoc loads
  - [ ] All endpoints are visible

- [ ] **Authentication Flow**
  - [ ] Register new user
  - [ ] Login with credentials
  - [ ] Receive JWT token
  - [ ] Use token to access protected endpoints

- [ ] **CRUD Operations**
  - [ ] Create todo
  - [ ] List todos
  - [ ] Update todo
  - [ ] Delete todo

### Performance Check
- [ ] Response time < 2 seconds for most requests
- [ ] No memory leaks (monitor over time)
- [ ] Database queries are efficient

### Security Check
- [ ] SECRET_KEY is secure (32+ characters)
- [ ] No secrets in code or logs
- [ ] CORS configured properly (not `["*"]` in production)
- [ ] HTTPS enabled (automatic on HF Spaces)
- [ ] Authentication required for protected endpoints

## Troubleshooting Guide

### Build Fails
- [ ] Check logs for specific error
- [ ] Verify Dockerfile syntax
- [ ] Ensure all dependencies in requirements.txt
- [ ] Check Python version compatibility

### Database Errors
- [ ] Verify DATABASE_URL is set correctly
- [ ] Check Alembic migrations ran successfully
- [ ] Ensure `/app/data/` directory exists
- [ ] Review migration files in `alembic/versions/`

### Authentication Issues
- [ ] Verify SECRET_KEY is set in Space secrets
- [ ] Check token expiration settings
- [ ] Test with fresh registration
- [ ] Review JWT configuration in `app/core/config.py`

### CORS Errors
- [ ] Update BACKEND_CORS_ORIGINS in Space secrets
- [ ] Include frontend domain in allowed origins
- [ ] Check browser console for specific CORS error
- [ ] Verify middleware configuration in `app/main.py`

## Maintenance Checklist

### Regular Tasks
- [ ] Monitor Space status weekly
- [ ] Check logs for errors
- [ ] Update dependencies monthly
- [ ] Backup database (if using persistent storage)
- [ ] Review and rotate SECRET_KEY periodically

### Updates
- [ ] Test changes locally first
- [ ] Commit and push to HF Space
- [ ] Monitor build and deployment
- [ ] Verify functionality after update
- [ ] Rollback if issues occur

## Success Criteria

Your deployment is successful when:
- ✅ Space shows "Running" status
- ✅ Health endpoint returns `{"status": "healthy"}`
- ✅ API documentation accessible at `/docs`
- ✅ User registration and login work
- ✅ CRUD operations for todos work
- ✅ No errors in Space logs
- ✅ Response times are acceptable

## Next Steps After Deployment

1. **Document API URL**: Share with frontend team
2. **Update Frontend**: Point to new API endpoint
3. **Set Up Monitoring**: Use external service for uptime monitoring
4. **Configure Custom Domain** (Optional): Available on paid tiers
5. **Plan for Scaling**: Consider upgrade if traffic increases

## Support Resources

- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Community Forum**: https://discuss.huggingface.co
- **Deployment Guide**: See `DEPLOYMENT.md` for detailed instructions

## Notes

- SQLite data persists between deployments but is lost if Space is deleted
- Free tier may sleep after inactivity
- First request after sleep takes longer to respond
- Consider external PostgreSQL for production workloads
- Upgrade Space hardware if performance is insufficient

---

**Last Updated**: 2026-01-15
**Status**: Ready for Deployment ✅
