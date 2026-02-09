# Deploy Frontend to Vercel - Step by Step

## Prerequisites
- GitHub repository pushed: ✅ https://github.com/sysylvia/rlhf-formats-pilot
- Backend deployed on Railway: ✅ (get URL first)
- Vercel account (free tier available)

## Step 1: Create Vercel Account

1. Go to **https://vercel.com**
2. Click **"Sign Up"**
3. Sign up with GitHub
4. Authorize Vercel to access your repositories

## Step 2: Import Project

1. Click **"Add New..."** → **"Project"**
2. Find and select: **`sysylvia/rlhf-formats-pilot`**
3. Click **"Import"**

## Step 3: Configure Project

### Framework Preset
- Select: **"Other"** (we're using vanilla HTML/JS)

### Root Directory
- Click **"Edit"** next to Root Directory
- Enter: `frontend`
- ✅ Confirm

### Build Settings
Leave these as default:
- **Build Command:** (leave empty)
- **Output Directory:** (leave empty)
- **Install Command:** (leave empty)

We're serving static files, no build needed.

## Step 4: Environment Variables (Optional)

We're using client-side JavaScript, so no server env vars needed. The API URL is hardcoded in `frontend/shared/api.js`.

## Step 5: Deploy

1. Click **"Deploy"**
2. Vercel will deploy in ~30 seconds
3. Watch the deployment logs

## Step 6: Get Your Frontend URL

After deployment:
1. Copy your Vercel URL: `https://your-project.vercel.app`

Example: `https://rlhf-formats-pilot.vercel.app`

## Step 7: Update API Configuration

Now that you have both URLs, connect them:

### Update Frontend API URL

1. **Edit** `frontend/shared/api.js`:
```javascript
const API_BASE_URL = 'https://your-backend.railway.app/api';
```

2. **Commit and push:**
```bash
cd /home/sean/.openclaw/workspace/rlhf-formats-pilot
# Edit the file first
git add frontend/shared/api.js
git commit -m "Update API URL for production backend"
git push
```

Vercel will auto-deploy the update (~30 seconds).

### Update Backend CORS

Go back to Railway:
1. Open your backend service
2. Go to **Variables** tab
3. Update or add:
   - `FRONTEND_URL` = `https://your-project.vercel.app`

Railway will restart with new CORS settings.

## Step 8: Test End-to-End

1. **Visit:** `https://your-project.vercel.app/?test=1`
2. Should see landing page
3. Click "Begin Study"
4. Should register participant and proceed

Test the flow:
- ✅ Landing page loads
- ✅ Registration works (check browser console for API calls)
- ✅ Instructions page loads
- ✅ Annotation interface loads
- ✅ Can submit annotation
- ✅ Completion code displays

## Step 9: Configure Custom Domain (Optional)

### Option A: Vercel-provided domain
You already have: `https://your-project.vercel.app`

### Option B: Custom domain
1. Go to Project **Settings** → **Domains**
2. Add your domain (e.g., `rlhf-pilot.yoursite.com`)
3. Update DNS records as instructed
4. Vercel auto-provisions SSL

## Step 10: Setup for Prolific

Your Prolific study URL will be:
```
https://your-project.vercel.app/?PROLIFIC_PID={{%PROLIFIC_PID%}}
```

Prolific replaces `{{%PROLIFIC_PID%}}` with actual participant IDs.

### Test with dummy ID:
```
https://your-project.vercel.app/?PROLIFIC_PID=TEST_12345
```

Should register and proceed normally.

## Automatic Deployments

✅ **Enabled by default**

Every push to `main` branch triggers:
1. Vercel deployment (~30 seconds)
2. Railway deployment (~2-3 minutes)

Monitor deployments:
- **Vercel:** Dashboard → Deployments
- **Railway:** Dashboard → Deployments

## Performance Optimization (Optional)

Vercel handles these automatically:
- ✅ Global CDN distribution
- ✅ Automatic HTTPS
- ✅ Compression (gzip/brotli)
- ✅ Edge caching for static files

For production, consider:
- Minify HTML/JS (add build step)
- Optimize images (if adding any)
- Enable Vercel Analytics

## Troubleshooting

### "API calls failing"
**Check:**
1. Backend URL correct in `frontend/shared/api.js`?
2. Backend health endpoint works: `curl https://your-backend.railway.app/health`
3. CORS configured: `FRONTEND_URL` set in Railway?
4. Browser console for detailed errors

### "Page not found (404)"
**Check:**
1. Root directory set to `frontend` in Vercel?
2. `index.html` exists in frontend folder?
3. Deployment logs for errors

### "Registration fails"
**Check:**
1. Backend `/api/participants/register` endpoint works
2. Test with curl:
```bash
curl -X POST https://your-backend.railway.app/api/participants/register \
  -H "Content-Type: application/json" \
  -d '{"prolific_pid":"TEST_123"}'
```
3. Should return participant info

### CORS Errors
```
Access-Control-Allow-Origin
```

**Fix:**
1. Set `FRONTEND_URL` in Railway env vars
2. Restart Railway service
3. Or temporarily set to `*` for testing

## Monitoring

### Vercel Analytics (Free)
1. Project Settings → Analytics
2. Enable Web Analytics
3. View page views, performance metrics

### Custom Monitoring
Add your own:
- Google Analytics
- Sentry for error tracking
- Custom logging

## Cost

- **Free Tier (Hobby):** 
  - 100GB bandwidth/month
  - Unlimited sites
  - Free HTTPS
  - Perfect for pilot study

- **Pro Plan ($20/mo):**
  - 1TB bandwidth
  - Advanced analytics
  - Not needed for pilot

Your pilot should run entirely on free tier.

## Security Checklist

Before going live:
- [ ] Backend CORS restricted to Vercel domain
- [ ] Test participant flow end-to-end
- [ ] Verify completion codes generate properly
- [ ] Check database persistence (Railway volume if needed)
- [ ] Test on desktop browsers (Chrome, Firefox, Safari)
- [ ] Prolific URL format correct
- [ ] IRB approval obtained (if required)

## Next Steps

1. ✅ Frontend deployed on Vercel
2. ✅ Backend deployed on Railway
3. ✅ URLs connected (API + CORS)
4. → Test complete participant flow
5. → Load real prompts (replace 3 examples)
6. → Create Prolific study
7. → Launch mini-pilot (5 participants, $150)
8. → Full pilot (10 participants, $600-800)

## URLs Summary

After deployment, you'll have:

```
Frontend:  https://your-project.vercel.app
Backend:   https://your-backend.railway.app
GitHub:    https://github.com/sysylvia/rlhf-formats-pilot

Prolific:  https://your-project.vercel.app/?PROLIFIC_PID={{%PROLIFIC_PID%}}
Test:      https://your-project.vercel.app/?test=1
```

## Support

- Vercel Docs: https://vercel.com/docs
- Vercel Discord: https://discord.gg/vercel
- GitHub Issues: https://github.com/sysylvia/rlhf-formats-pilot/issues

---

**Ready to deploy?** Start with Railway (backend), then Vercel (frontend).
