# Quick Deploy Guide - CLI Method

✅ **Vercel CLI installed**  
⚠️ **Railway CLI requires sudo** (use web dashboard instead)

## Deploy Frontend (Vercel CLI)

### Step 1: Login to Vercel
```bash
cd /home/sean/.openclaw/workspace/rlhf-formats-pilot/frontend
vercel login
```

This will open a browser for authentication.

### Step 2: Deploy Frontend
```bash
vercel --prod
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Your account
- **Link to existing project?** No
- **Project name?** `rlhf-formats-pilot` (or your choice)
- **Directory?** `.` (current directory, we're already in frontend/)
- **Want to override settings?** No

Vercel will deploy and give you a URL like:
```
https://rlhf-formats-pilot.vercel.app
```

**Save this URL!** ✍️

## Deploy Backend (Railway Dashboard)

Railway CLI needs sudo, so use the web dashboard:

### Step 1: Go to Railway
1. Visit: **https://railway.app/new**
2. Click **"Deploy from GitHub repo"**
3. Select: **`sysylvia/rlhf-formats-pilot`**

### Step 2: Configure
1. Railway detects Node.js automatically
2. Set **Root Directory:** `backend`
3. Click **"Deploy"**

### Step 3: Generate Domain
1. Wait for first deployment (~2-3 min)
2. Go to **Settings** → **Networking**
3. Click **"Generate Domain"**
4. Copy URL: `https://rlhf-pilot-backend.up.railway.app`

**Save this URL!** ✍️

### Step 4: Initialize Database
**Option A - Add startup code (recommended):**

I can help you add auto-initialization to the backend. This will create the database on first run.

**Option B - Manual via Railway dashboard:**
1. Click your service → **Settings** → **Variables**
2. Add these commands to run once (via Railway CLI if you install it with sudo later)

## Connect Frontend to Backend

Once both are deployed:

### Update API URL
```bash
cd /home/sean/.openclaw/workspace/rlhf-formats-pilot
```

Edit `frontend/shared/api.js` and replace:
```javascript
const API_BASE_URL = 'https://YOUR-RAILWAY-URL.railway.app/api';
```

Then redeploy frontend:
```bash
cd frontend
vercel --prod
```

### Update CORS
In Railway dashboard:
1. Go to your service → **Variables**
2. Add: `FRONTEND_URL` = `https://your-vercel-url.vercel.app`

## Test Deployment

### Backend Health Check
```bash
curl https://YOUR-RAILWAY-URL.railway.app/health
```

Should return:
```json
{"status":"healthy","database":"connected","timestamp":"..."}
```

### Frontend Test
Visit: `https://YOUR-VERCEL-URL.vercel.app/?test=1`

Should see landing page and be able to register.

### Full Flow Test
1. Visit frontend URL with `?test=1`
2. Click "Begin Study"
3. Go through instructions
4. Complete 1-2 annotations
5. Get completion code

## What's Next?

After successful deployment:

1. **Load Real Prompts** - Replace 3 examples with 100+ real prompts
2. **Test with 1-2 people** - Verify everything works
3. **Create Prolific Study** - Set up recruitment
4. **Launch Mini-Pilot** - 5 participants ($150)
5. **Full Pilot** - 10 participants ($600-800)

## Deployment URLs Template

Fill in your URLs:

```
Frontend (Vercel):  https://_______________.vercel.app
Backend (Railway):  https://_______________.railway.app
GitHub Repo:        https://github.com/sysylvia/rlhf-formats-pilot

Prolific URL:       https://_______________.vercel.app/?PROLIFIC_PID={{%PROLIFIC_PID%}}
Test URL:           https://_______________.vercel.app/?test=1
```

## Need Help?

- See `DEPLOY_VERCEL.md` for detailed Vercel instructions
- See `DEPLOY_RAILWAY.md` for detailed Railway instructions
- Check `DEPLOYMENT.md` for troubleshooting

---

**Ready?** Let's start with frontend deployment using Vercel CLI! 🚀
