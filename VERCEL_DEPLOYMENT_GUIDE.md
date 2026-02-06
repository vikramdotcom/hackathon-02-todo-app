# Vercel Deployment Guide - Todo App with AI Chatbot

## 🚀 Quick Deployment Steps

### Step 1: Connect GitHub Repository to Vercel

1. **Go to Vercel:** https://vercel.com/new
2. **Sign in/Sign up:**
   - Use your GitHub account for seamless integration
   - Or use GitLab, Bitbucket, or email

3. **Import Git Repository:**
   - Click "Add New..." → "Project"
   - Select "Import Git Repository"
   - Choose: `vikramdotcom/hackathon-02-todo-app`
   - Click "Import"

### Step 2: Configure Project Settings

**Framework Preset:** Next.js (auto-detected)

**Root Directory:**
```
phase-3-ai-chatbot/frontend
```
⚠️ **IMPORTANT:** Click "Edit" next to Root Directory and set this path!

**Build Settings:**
- Build Command: `npm run build` (default)
- Output Directory: `.next` (default)
- Install Command: `npm install` (default)
- Development Command: `npm run dev` (default)

### Step 3: Environment Variables

Click "Environment Variables" and add:

| Name | Value | Environment |
|------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend-url.com/api/v1` | Production |

**Backend URL Options:**
- If deploying backend to Hugging Face: `https://your-space.hf.space/api/v1`
- If deploying backend elsewhere: Use that URL
- For testing: You can use `http://localhost:8001/api/v1` (won't work in production)

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for build to complete
3. You'll get a URL like: `https://your-app.vercel.app`

---

## 🔧 Post-Deployment Configuration

### Update Backend CORS Settings

After deployment, update your backend to allow requests from your Vercel domain:

**In `phase-3-ai-chatbot/backend/app/main.py`:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",  # Add your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Set Up Custom Domain (Optional)

1. Go to your project in Vercel Dashboard
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

---

## 🎯 Deployment Checklist

- [ ] Repository connected to Vercel
- [ ] Root directory set to `phase-3-ai-chatbot/frontend`
- [ ] Environment variable `NEXT_PUBLIC_API_URL` configured
- [ ] First deployment successful
- [ ] Backend CORS updated with Vercel URL
- [ ] Application accessible and working
- [ ] Dark mode toggle working
- [ ] Chatbot functionality tested

---

## 🔄 Automatic Deployments

Once connected, Vercel will automatically:
- Deploy every push to `main` branch (Production)
- Create preview deployments for pull requests
- Show deployment status in GitHub

---

## 📊 Monitoring & Logs

**View Deployment Logs:**
1. Go to Vercel Dashboard
2. Select your project
3. Click on a deployment
4. View "Build Logs" and "Function Logs"

**Analytics:**
- Vercel provides built-in analytics
- View page views, performance metrics, and more

---

## 🐛 Troubleshooting

### Build Fails
- Check build logs in Vercel dashboard
- Ensure all dependencies are in `package.json`
- Verify Node.js version compatibility

### API Connection Issues
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend CORS settings
- Ensure backend is deployed and accessible

### Environment Variables Not Working
- Environment variables must start with `NEXT_PUBLIC_` to be accessible in browser
- Redeploy after adding/changing environment variables

---

## 🚀 Alternative: Deploy Backend to Vercel

You can also deploy the FastAPI backend to Vercel:

1. Create `vercel.json` in `phase-3-ai-chatbot/backend/`:
```json
{
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ]
}
```

2. Create `requirements.txt` with all dependencies
3. Deploy backend separately to Vercel
4. Update frontend `NEXT_PUBLIC_API_URL` with backend Vercel URL

---

## 📝 Notes

- **Free Tier:** Vercel's free tier is generous for hobby projects
- **Build Time:** First build takes 2-3 minutes, subsequent builds are faster
- **Serverless:** Frontend is deployed as serverless functions
- **CDN:** Static assets are served via Vercel's global CDN
- **HTTPS:** Automatic HTTPS for all deployments

---

## 🎉 Success!

Once deployed, your application will be live at:
- **Production:** `https://your-app.vercel.app`
- **Preview:** Unique URL for each PR

Share your deployment URL and enjoy your AI-powered Todo App! 🚀
