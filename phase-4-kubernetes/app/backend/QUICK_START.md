# Quick Start - Hugging Face Deployment

## 🚀 Deploy in 3 Steps

### Step 1: Clean Up (2 minutes)
```bash
cd phase-2-web-app/backend

# Remove old database files
rm -f *.db

# Run pre-deployment script
scripts\prepare_deployment.bat  # Windows
# OR
bash scripts/prepare_deployment.sh  # Linux/Mac
```

### Step 2: Commit & Push (1 minute)
```bash
git add .
git commit -m "fix: permanent SQLite migration fix for Hugging Face deployment"
git push
```

### Step 3: Deploy to Hugging Face (5 minutes)
1. Go to https://huggingface.co/spaces
2. Create new Space or update existing
3. Set environment variables:
   ```
   DATABASE_URL=sqlite:///./todo_app.db
   SECRET_KEY=<your-secret-key>
   ENVIRONMENT=production
   ```
4. Connect your GitHub repository
5. Deploy!

---

## ✅ Verify Deployment

```bash
# Replace with your Space URL
export HF_URL="https://your-space.hf.space"

# Test health
curl $HF_URL/health

# Test API docs
curl $HF_URL/docs

# Test registration
curl -X POST "$HF_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"SecurePass123!"}'
```

---

## 📚 Full Documentation

- **Detailed Guide:** `HUGGINGFACE_DEPLOYMENT.md`
- **Technical Summary:** `DEPLOYMENT_SUMMARY.md`
- **This Quick Start:** `QUICK_START.md`

---

## 🆘 Troubleshooting

**Error: "near 'CONSTRAINT': syntax error"**
→ Old database file exists. Run: `rm -f *.db` and redeploy

**Error: "No such table: users"**
→ Check logs for migration errors. Database should auto-initialize on startup.

**Email validation not working**
→ Validation is now in Python layer (app/models/user.py). Check Pydantic validators.

---

## 🎯 What Was Fixed

✅ Removed PostgreSQL operators from migration
✅ Added email validation to Python layer
✅ Enabled SQLite batch mode in Alembic
✅ Added automatic database recovery on startup
✅ Created comprehensive deployment scripts

**Status:** Production-ready for Hugging Face Spaces
