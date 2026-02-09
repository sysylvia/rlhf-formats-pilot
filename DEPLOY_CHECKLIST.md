# Deployment Checklist - Ready When You Are!

## ✅ What's Done

- [x] Git repository created and pushed to GitHub
- [x] Backend code complete (Node.js API + SQLite)
- [x] Frontend code complete (3 annotation interfaces)
- [x] Power analysis complete (within-subjects recommended)
- [x] All documentation written
- [x] Vercel CLI installed
- [x] Comprehensive deployment guides created

**GitHub Repo:** https://github.com/sysylvia/rlhf-formats-pilot

## 📋 What's Left: Deploy to Production

### Step 1: Deploy Frontend (Vercel) - 5 minutes

**URL:** https://vercel.com/new

1. Click "Import Project"
2. Select: `sysylvia/rlhf-formats-pilot`
3. Configure:
   - Framework: **Other**
   - Root Directory: **`frontend`** ← Important!
   - Leave build commands empty
4. Click "Deploy"
5. **Save your URL:** `https://____________.vercel.app`

**Detailed guide:** See `DEPLOY_VERCEL.md` in repo

### Step 2: Deploy Backend (Railway) - 10 minutes

**URL:** https://railway.app/new

1. Click "Deploy from GitHub repo"
2. Select: `sysylvia/rlhf-formats-pilot`
3. Configure:
   - Root Directory: **`backend`** ← Important!
   - Auto-detects Node.js (leave defaults)
4. Click "Deploy"
5. Wait for first deployment (~2-3 min)
6. Settings → Networking → "Generate Domain"
7. **Save your URL:** `https://____________.railway.app`

**Detailed guide:** See `DEPLOY_RAILWAY.md` in repo

### Step 3: Connect Frontend to Backend - 5 minutes

After both deployed:

1. **Update API URL in frontend:**
   ```bash
   cd /home/sean/.openclaw/workspace/rlhf-formats-pilot
   # Edit frontend/shared/api.js
   # Change: const API_BASE_URL = 'https://YOUR-RAILWAY-URL.railway.app/api';
   git add frontend/shared/api.js
   git commit -m "Update API URL for production"
   git push
   ```
   Vercel will auto-deploy the update.

2. **Update CORS in backend:**
   - Go to Railway dashboard
   - Your service → Variables
   - Add: `FRONTEND_URL` = `https://your-vercel-url.vercel.app`

### Step 4: Initialize Database - 2 minutes

**Option A - Automatic (Recommended):**

Add this to `backend/src/server.js` at the top (before app setup):
```javascript
// Auto-initialize database on first run
const fs = require('fs');
const path = require('path');
const dbPath = path.join(__dirname, '../data/pilot.db');
if (!fs.existsSync(dbPath)) {
    const { initializeDatabase } = require('./utils/initDb');
    const { seedPrompts } = require('./utils/seedPrompts');
    initializeDatabase();
    seedPrompts();
}
```

Then push:
```bash
git add backend/src/server.js
git commit -m "Auto-initialize database on first run"
git push
```

Railway will redeploy and create the database automatically.

**Option B - Manual:**
- Install Railway CLI locally
- Run: `railway run npm run init-db`

### Step 5: Test Deployment - 5 minutes

1. **Backend health check:**
   ```bash
   curl https://your-railway-url.railway.app/health
   ```
   Should return: `{"status":"healthy","database":"connected",...}`

2. **Frontend test:**
   Visit: `https://your-vercel-url.vercel.app/?test=1`
   - Landing page loads ✓
   - Click "Begin Study" ✓
   - Register participant ✓
   - View instructions ✓
   - Complete annotation ✓
   - Get completion code ✓

3. **Check stats:**
   ```bash
   curl https://your-railway-url.railway.app/api/study/stats
   ```
   Should show 1 participant, 1+ annotation.

## ⏭️ After Deployment

### Load Real Prompts (Before Launch)

Replace the 3 example prompts with 100+ real prompts:

```bash
# Option 1: Bulk add via API
curl -X POST https://your-railway-url.railway.app/api/prompts/bulk \
  -H "Content-Type: application/json" \
  -d @prompts.json

# Option 2: One at a time
curl -X POST https://your-railway-url.railway.app/api/prompts \
  -H "Content-Type: application/json" \
  -d '{"text":"...","response_a":"...","response_b":"...",...}'
```

**Prompt format:**
```json
{
  "text": "Write a haiku about...",
  "response_a": "Response text...",
  "response_b": "Response text...",
  "response_c": "Response text...",  // For BWS
  "response_d": "Response text...",  // For BWS
  "source": "gpt4",
  "category": "creative"
}
```

### Configure Study Settings

Set within-subjects vs between-subjects:
```bash
# Within-subjects (recommended)
curl -X POST https://your-railway-url.railway.app/api/study/config \
  -H "Content-Type: application/json" \
  -d '{"key":"design_type","value":"within"}'

# Annotations per format
curl -X POST https://your-railway-url.railway.app/api/study/config \
  -H "Content-Type: application/json" \
  -d '{"key":"annotations_per_format","value":"15"}'
```

### Create Prolific Study

**Study URL:**
```
https://your-vercel-url.vercel.app/?PROLIFIC_PID={{%PROLIFIC_PID%}}
```

**Settings:**
- Device: Desktop only
- Time: 15-20 minutes
- Payment: $3-4 ($12-15/hour rate)
- Completion type: URL

**Description:** See `DEPLOY_VERCEL.md` for example text

### Mini-Pilot (Optional but Recommended)

Before full launch:
- 5 participants × 45-60 annotations
- Budget: ~$150
- Purpose: Validate interfaces, catch bugs, test data export

### Full Pilot

**Within-subjects (recommended):**
- 6-10 participants × 45-60 annotations each
- Budget: $600-800
- Statistical power: 80%+ for detecting 15-30% differences

**Between-subjects:**
- 30 participants × 15-20 annotations each
- Budget: $900-1,200
- Statistical power: 65-70% for detecting 30% differences

## 📊 Monitoring & Data Export

### During Study

Check stats in real-time:
```bash
curl https://your-railway-url.railway.app/api/study/stats
```

### After Study

Export all data:
```bash
curl https://your-railway-url.railway.app/api/study/export/participants > participants.json
curl https://your-railway-url.railway.app/api/study/export/annotations > annotations.json
curl https://your-railway-url.railway.app/api/study/export/prompts > prompts.json
```

Import into R/Python for analysis.

## 📚 Documentation Reference

All in your GitHub repo:

- **`README.md`** - Project overview
- **`DEPLOY_VERCEL.md`** - Complete Vercel guide
- **`DEPLOY_RAILWAY.md`** - Complete Railway guide
- **`QUICK_DEPLOY.md`** - Fast track deployment
- **`DEPLOYMENT.md`** - Original deployment guide
- **`PROJECT_README.md`** - Full documentation
- **`backend/README.md`** - API documentation

## 🆘 Troubleshooting

### "API calls failing"
- Check backend health: `/health`
- Verify API_BASE_URL in `frontend/shared/api.js`
- Check CORS: `FRONTEND_URL` set in Railway?

### "Database not found"
- Add auto-init code (see Step 4)
- Or use Railway CLI: `railway run npm run init-db`

### "Page not found"
- Root directory set to `frontend` in Vercel?
- Check deployment logs

### Need Help?
- Check detailed guides in repo
- GitHub issues: https://github.com/sysylvia/rlhf-formats-pilot/issues
- Or ask Scout!

## ⏱️ Time Estimate

- Deploy frontend: **5 min**
- Deploy backend: **10 min**
- Connect them: **5 min**
- Test: **5 min**
- **Total: ~25 minutes**

Then you're live and ready for pilot testing!

---

**GitHub Repo:** https://github.com/sysylvia/rlhf-formats-pilot  
**Status:** Code complete, documentation complete, ready to deploy!  
**Next:** Deploy to Vercel + Railway → Load prompts → Launch pilot
