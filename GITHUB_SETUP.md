# GitHub Setup Instructions

## Repository Created ✅

Local git repository initialized with all project files committed.

**Commit:** `ba2d679` - "Initial commit: RLHF formats comparison pilot platform"  
**Files committed:** 52 files, 12,621 insertions

## To Push to GitHub

### Option 1: Create New Repository on GitHub (Recommended)

1. **Go to GitHub:** https://github.com/new
2. **Repository name:** `rlhf-formats-pilot` (or your preferred name)
3. **Description:** "Experimental platform for comparing RLHF feedback elicitation formats"
4. **Visibility:** Public or Private (your choice)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. **Click "Create repository"**

7. **Add remote and push:**
```bash
cd /home/sean/.openclaw/workspace/rlhf-formats-pilot
git remote add origin https://github.com/YOUR_USERNAME/rlhf-formats-pilot.git
git branch -M main
git push -u origin main
```

### Option 2: Push to Existing Repository

If you already have a repository:
```bash
cd /home/sean/.openclaw/workspace/rlhf-formats-pilot
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

## Repository Contents

```
✅ Backend (Node.js/Express + SQLite)
✅ Frontend (HTML/JS - 3 annotation interfaces)
✅ Power analysis scripts (Python)
✅ Visualizations (PNG files)
✅ Documentation (README, DEPLOYMENT, API docs)
✅ .gitignore (excludes node_modules, DB files, .env)
```

## What's NOT in the Repository (by design)

- `node_modules/` - Dependencies (excluded via .gitignore)
- `backend/data/*.db` - Database files (excluded)
- `.env` - Environment variables (excluded, .env.example provided)
- Build artifacts

Users will run `npm install` to get dependencies after cloning.

## After Pushing

### For Deployment

**Backend (Railway):**
1. Connect your GitHub repo to Railway
2. Auto-deploys on push to main branch
3. Set environment variables in Railway dashboard

**Frontend (Vercel):**
1. Import project from GitHub
2. Root directory: `frontend/`
3. Auto-deploys on push

See `DEPLOYMENT.md` for detailed instructions.

### Collaboration

Add collaborators:
- Go to repo Settings → Collaborators
- Add by GitHub username

### Repository Settings (Recommended)

**Branch Protection:**
- Settings → Branches → Add rule for `main`
- Require pull request reviews (optional)
- Require status checks (optional)

**Topics/Tags:**
Add relevant topics for discoverability:
- `rlhf`
- `machine-learning`
- `human-feedback`
- `experimental-design`
- `annotation-platform`

## Questions?

Check `README.md` for project overview and quick start.
Check `DEPLOYMENT.md` for hosting instructions.
Check `PROJECT_README.md` for comprehensive documentation.
