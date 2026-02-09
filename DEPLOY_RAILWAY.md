# Deploy Backend to Railway - Step by Step

## Prerequisites
- GitHub repository pushed: ✅ https://github.com/sysylvia/rlhf-formats-pilot
- Railway account (free tier available)

## Step 1: Create Railway Account

1. Go to **https://railway.app**
2. Click **"Login"** or **"Start a New Project"**
3. Sign up/login with GitHub
4. Authorize Railway to access your repositories

## Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select: **`sysylvia/rlhf-formats-pilot`**
4. Railway will detect your repository

## Step 3: Configure Service

Railway should auto-detect Node.js, but verify:

1. **Root Directory:** Leave blank (Railway will use `/backend` based on file structure)
2. **Build Command:** Should auto-detect `npm install`
3. **Start Command:** Should auto-detect `npm start`

If Railway doesn't auto-detect properly:
- Click on the service → **Settings** → **Build & Deploy**
- **Root Directory:** `backend`
- **Build Command:** `npm install && npm run init-db`
- **Start Command:** `npm start`

## Step 4: Environment Variables

Railway automatically provides `PORT`, but you may want to set:

1. Click your service → **Variables** tab
2. Add variables:
   - `NODE_ENV` = `production`
   - `FRONTEND_URL` = `*` (we'll update this after deploying frontend)

Leave `PORT` blank - Railway assigns this automatically.

## Step 5: Deploy

1. Railway will automatically deploy on push
2. First deployment will take 2-3 minutes
3. Watch the **Deployments** tab for progress

## Step 6: Initialize Database

After first deployment, you need to initialize the database:

### Option A: Railway CLI (if available)
```bash
railway login
railway link
railway run npm run init-db
railway run npm run seed-prompts
```

### Option B: Temporary Script (Recommended)

Add this to your backend startup temporarily:

**Edit `backend/src/server.js`**, add at the top:
```javascript
// One-time database initialization
const { initializeDatabase } = require('./utils/initDb');
const { seedPrompts } = require('./utils/seedPrompts');

// Check if database exists, initialize if not
const fs = require('fs');
const path = require('path');
const dbPath = path.join(__dirname, '../data/pilot.db');
if (!fs.existsSync(dbPath)) {
    console.log('Database not found, initializing...');
    initializeDatabase();
    seedPrompts();
}
```

Then commit and push:
```bash
git add backend/src/server.js
git commit -m "Auto-initialize database on first run"
git push
```

Railway will auto-deploy and initialize the database.

**After first successful deployment, remove this code** to avoid re-initialization.

## Step 7: Get Your Backend URL

1. Go to your Railway service dashboard
2. Click **Settings** → **Networking**
3. Click **Generate Domain**
4. Copy your URL: `https://your-app.railway.app`

Example: `https://rlhf-pilot-backend.up.railway.app`

## Step 8: Test Your Backend

```bash
curl https://your-app.railway.app/health
```

Should return:
```json
{"status":"healthy","database":"connected","timestamp":"..."}
```

Test stats endpoint:
```bash
curl https://your-app.railway.app/api/study/stats
```

## Step 9: Update Frontend Configuration

After getting your backend URL, update the frontend:

1. Edit `frontend/shared/api.js`:
```javascript
const API_BASE_URL = 'https://your-app.railway.app/api';
```

2. Commit and push:
```bash
git add frontend/shared/api.js
git commit -m "Update API URL for production"
git push
```

## Troubleshooting

### "Build failed"
- Check **Logs** tab for error messages
- Verify `package.json` is in `backend/` directory
- Ensure all dependencies are listed in `package.json`

### "Database not found"
- Railway provides ephemeral storage by default
- For persistent storage, add a Volume:
  - Settings → Storage → Add Volume
  - Mount path: `/app/backend/data`
  - This persists your SQLite database across deployments

### "Port already in use"
- Railway assigns PORT automatically
- Remove `PORT=3001` from `.env` if present
- Use `process.env.PORT || 3000` in server.js (already configured)

### CORS errors
- Update `FRONTEND_URL` environment variable with your Vercel URL
- Or keep as `*` for development (less secure)

## Cost

- **Free Tier:** $5 credit/month (~500 hours)
- **Hobby Plan:** $5/month for sustained usage
- **Pro Plan:** $20/month for production

Your pilot should run fine on free tier (~3-5 days of active use).

## Next Steps

1. ✅ Backend deployed on Railway
2. → Deploy frontend on Vercel (see `DEPLOY_VERCEL.md`)
3. → Update CORS settings with Vercel URL
4. → Test end-to-end flow
5. → Launch pilot on Prolific

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/sysylvia/rlhf-formats-pilot/issues
