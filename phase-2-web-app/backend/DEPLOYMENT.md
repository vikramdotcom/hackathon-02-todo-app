# Deployment Guide - Hugging Face Spaces

This guide walks you through deploying the Todo App backend API to Hugging Face Spaces.

## Prerequisites

- Hugging Face account (sign up at https://huggingface.co)
- Git installed locally
- Backend code ready for deployment

## Step 1: Create a New Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Configure your Space:
   - **Space name**: `todo-app-api` (or your preferred name)
   - **License**: Choose appropriate license (e.g., MIT)
   - **Select SDK**: Choose **Docker**
   - **Space hardware**: CPU basic (free tier) is sufficient
   - **Visibility**: Public or Private (your choice)
4. Click "Create Space"

## Step 2: Configure Environment Variables

Before pushing code, set up required environment variables:

1. Go to your Space settings (Settings tab)
2. Scroll to "Repository secrets"
3. Add the following secrets:

### Required Secrets

**SECRET_KEY** (Required)
```bash
# Generate a secure secret key:
openssl rand -hex 32
```
Copy the output and add it as `SECRET_KEY`

**DATABASE_URL** (Required)
```
sqlite:///./data/todo_app.db
```

### Optional Configuration

**ENVIRONMENT**
```
production
```

**ACCESS_TOKEN_EXPIRE_MINUTES**
```
1440
```

**BACKEND_CORS_ORIGINS**
```json
["*"]
```
Note: For production, replace `["*"]` with specific frontend URLs like `["https://your-frontend.hf.space"]`

## Step 3: Push Code to Hugging Face

### Option A: Using Git (Recommended)

```bash
# Navigate to backend directory
cd phase-2-web-app/backend

# Initialize git if not already done
git init

# Add Hugging Face Space as remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME

# Add all files
git add .

# Commit
git commit -m "Initial deployment to Hugging Face Spaces"

# Push to Hugging Face
git push hf main
```

### Option B: Using Hugging Face Web Interface

1. Go to your Space's "Files" tab
2. Click "Add file" → "Upload files"
3. Upload all files from the `backend` directory
4. Ensure these files are included:
   - `Dockerfile`
   - `README.md`
   - `requirements.txt`
   - `alembic.ini`
   - `app/` directory (all files)
   - `alembic/` directory (all files)

## Step 4: Monitor Deployment

1. Go to your Space's main page
2. Watch the "Building" logs in real-time
3. The build process will:
   - Build Docker image
   - Install dependencies
   - Run database migrations
   - Start the FastAPI server

Expected build time: 3-5 minutes

## Step 5: Verify Deployment

Once the Space shows "Running":

### Test Health Endpoint
```bash
curl https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/health
```

Expected response:
```json
{"status": "healthy"}
```

### Access API Documentation
Visit: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/docs`

You should see the interactive Swagger UI with all API endpoints.

### Test User Registration
```bash
curl -X POST "https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

### Test Login
```bash
curl -X POST "https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePass123!"
```

## Troubleshooting

### Build Fails

**Check logs**: Go to Space → "Logs" tab to see detailed error messages

**Common issues**:
- Missing dependencies in `requirements.txt`
- Syntax errors in Dockerfile
- Port configuration issues

**Solution**: Fix the issue locally, commit, and push again

### Database Errors

**Issue**: "No such table" errors

**Solution**: Ensure Alembic migrations run successfully
- Check that `alembic.ini` is present
- Verify `alembic/versions/` contains migration files
- Check Dockerfile CMD includes `alembic upgrade head`

### Authentication Errors

**Issue**: "Could not validate credentials"

**Solution**: Verify `SECRET_KEY` is set in Space secrets
- Must be at least 32 characters
- Should be generated with `openssl rand -hex 32`

### CORS Errors

**Issue**: Frontend can't connect due to CORS

**Solution**: Update `BACKEND_CORS_ORIGINS` in Space secrets
```json
["https://your-frontend-domain.com", "https://your-frontend.hf.space"]
```

### Space Keeps Restarting

**Issue**: Container crashes and restarts repeatedly

**Solution**:
- Check logs for Python errors
- Verify all required environment variables are set
- Ensure database migrations complete successfully

## Updating Your Deployment

To update your deployed API:

```bash
# Make changes to your code
# Commit changes
git add .
git commit -m "Update: description of changes"

# Push to Hugging Face
git push hf main
```

The Space will automatically rebuild and redeploy.

## Database Persistence

**Important**: With SQLite on Hugging Face Spaces:
- Data persists between deployments
- Database is stored in `/app/data/todo_app.db`
- If Space is deleted, all data is lost
- For production, consider external PostgreSQL database

## Performance Considerations

**Free Tier Limitations**:
- CPU basic (2 vCPU, 16GB RAM)
- May sleep after inactivity
- First request after sleep takes longer

**Upgrade Options**:
- CPU upgrade for better performance
- Persistent storage for guaranteed data retention
- Custom domains available on paid tiers

## Security Best Practices

1. **Never commit secrets**: Use Space secrets for sensitive data
2. **Use strong SECRET_KEY**: Generate with `openssl rand -hex 32`
3. **Configure CORS properly**: Don't use `["*"]` in production
4. **Enable HTTPS**: Hugging Face provides this automatically
5. **Regular updates**: Keep dependencies updated for security patches

## Monitoring

**Check Space Status**:
- Visit your Space URL
- Check `/health` endpoint
- Monitor logs in Space dashboard

**Set Up Alerts**:
- Hugging Face doesn't provide built-in alerts
- Consider external monitoring (UptimeRobot, Pingdom)

## Cost

**Free Tier**:
- Sufficient for development and small projects
- No credit card required

**Paid Tiers**:
- Start at $0.60/hour for upgraded hardware
- See https://huggingface.co/pricing for details

## Next Steps

After successful deployment:

1. **Update frontend**: Point your frontend to the new API URL
2. **Test all endpoints**: Use the `/docs` interface
3. **Set up monitoring**: Track uptime and performance
4. **Configure CORS**: Add your frontend domain
5. **Document API URL**: Share with your team

## Support

- Hugging Face Docs: https://huggingface.co/docs/hub/spaces
- Community Forum: https://discuss.huggingface.co
- GitHub Issues: Report bugs in your repository

## Example Space URL

After deployment, your API will be available at:
```
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space
```

API documentation:
```
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/docs
```
