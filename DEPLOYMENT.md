# RLHF Pilot Deployment Guide

## Architecture

```
Prolific → Frontend (Vercel) → Backend API (Railway) → SQLite Database
```

## Backend Deployment (Railway)

### Step 1: Prepare Repository
```bash
cd backend
git init
git add .
git commit -m "Initial commit"
```

### Step 2: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select the repository
4. Railway will auto-detect Node.js and use `railway.json` config
5. Set environment variables (if needed):
   - `NODE_ENV=production`
   - `FRONTEND_URL=https://your-frontend.vercel.app`

### Step 3: Initialize Database
After deployment, connect to Railway shell:
```bash
npm run init-db
npm run seed-prompts  # Optional: load example prompts
```

### Step 4: Get Backend URL
Copy your Railway app URL (e.g., `https://rlhf-pilot-backend.up.railway.app`)

## Frontend Deployment (Vercel)

### Step 1: Update API URL
Edit `frontend/shared/api.js`:
```javascript
const API_BASE_URL = 'https://your-backend.railway.app/api';
```

### Step 2: Deploy to Vercel
```bash
cd frontend
vercel
# Follow prompts, select "frontend" directory
```

Or use Vercel dashboard:
1. Go to [vercel.com](https://vercel.com)
2. "New Project" → Import from Git
3. Root directory: `frontend`
4. Deploy

### Step 3: Get Frontend URL
Copy your Vercel URL (e.g., `https://rlhf-pilot.vercel.app`)

### Step 4: Update CORS
Update backend `FRONTEND_URL` env variable in Railway to your Vercel URL.

## Prolific Integration

### Study URL Format
```
https://your-frontend.vercel.app/?PROLIFIC_PID={{%PROLIFIC_PID%}}
```

Prolific automatically replaces `{{%PROLIFIC_PID%}}` with participant IDs.

### Study Settings
- **Device Compatibility:** Desktop only
- **Estimated Time:** 15-20 minutes
- **Reward:** $3.00 - $4.00 (based on $12-15/hour)
- **Completion Code:** Auto-generated (format: `RLHF2026-XXXXXXXX`)

### Prolific Study Description Example
```
Title: Evaluate AI-Generated Responses (15-20 min)

Description:
Help us understand how people evaluate AI-generated responses. 
You'll compare and rate AI responses to various prompts using 
one or more evaluation methods.

Requirements:
- Native English speaker
- Desktop or laptop (mobile not supported)
- Quiet environment recommended

Completion:
You'll receive a unique completion code at the end. 
Paste it in Prolific to confirm completion and receive payment.
```

## Testing

### Local Testing
1. Start backend:
```bash
cd backend
npm run dev
```

2. Serve frontend (use a local server):
```bash
cd frontend
python3 -m http.server 8080
# Or: npx serve
```

3. Visit: `http://localhost:8080/?test=1`
   - `test=1` bypasses Prolific ID requirement

### Test Flow
1. Landing page → Registration
2. Instructions
3. Task(s) based on design (within/between)
4. Completion with code

## Data Export

### Via API
```bash
# Export all data
curl https://your-backend.railway.app/api/study/export/participants > participants.json
curl https://your-backend.railway.app/api/study/export/annotations > annotations.json
curl https://your-backend.railway.app/api/study/export/prompts > prompts.json
```

### Direct Database Access
Download SQLite database from Railway volume (if using persistent storage).

## Study Configuration

### Change Study Design (Within/Between)
```bash
curl -X POST https://your-backend.railway.app/api/study/config \
  -H "Content-Type: application/json" \
  -d '{"key": "design_type", "value": "within"}'
```

### Adjust Annotations Per Format
```bash
curl -X POST https://your-backend.railway.app/api/study/config \
  -H "Content-Type: application/json" \
  -d '{"key": "annotations_per_format", "value": "20"}'
```

### Enable/Disable Formats
```bash
curl -X POST https://your-backend.railway.app/api/study/config \
  -H "Content-Type: application/json" \
  -d '{"key": "formats_enabled", "value": "pairwise,bws"}'
```

## Monitoring

### Check Study Stats
```bash
curl https://your-backend.railway.app/api/study/stats
```

Returns:
```json
{
  "stats": {
    "total_participants": 25,
    "completed_participants": 18,
    "total_annotations": 450,
    "annotations_by_format": {
      "pairwise": 150,
      "bws": 150,
      "peer_prediction": 150
    },
    "prompts_count": 100
  }
}
```

### Health Check
```bash
curl https://your-backend.railway.app/health
```

## Cost Estimates

### Infrastructure
- **Railway (Backend):** Free tier ($5/month for sustained usage)
- **Vercel (Frontend):** Free tier (100GB bandwidth)
- **Total infrastructure:** $0-5/month

### Participants (Prolific)
- **Within-subjects** (10 labelers × 45-60 annotations): $600-800
- **Between-subjects** (30 labelers × 15-20 annotations): $900-1,200

## Security Notes

- No authentication required (study is anonymous)
- Prolific IDs used only for payment verification
- No sensitive data collected
- CORS restricted to frontend domain
- Consider adding rate limiting for production

## Troubleshotshooting

### "No participant ID found"
- Check Prolific URL includes `{{%PROLIFIC_PID%}}`
- For testing, use `?test=1`

### Backend connection failed
- Verify `API_BASE_URL` in `frontend/shared/api.js`
- Check CORS settings in backend
- Confirm Railway deployment is running

### Tasks not loading
- Check database has prompts: `/api/study/stats`
- Verify study_config: `/api/study/config`
- Check browser console for errors

## Support

Questions? Contact: [researcher email]
Repository: [GitHub URL]
