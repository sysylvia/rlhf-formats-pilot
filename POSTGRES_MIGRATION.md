# PostgreSQL Migration Guide

## What Changed

The backend has been migrated from SQLite to PostgreSQL with **experiment tracking** added for multi-study support.

### Key Changes:
1. **Database:** SQLite → PostgreSQL (better persistence on cloud platforms)
2. **Experiment Tracking:** New `experiments` table + `experiment_id` foreign keys throughout
3. **Data Isolation:** Each experiment's data is separate and queryable
4. **Dependencies:** `better-sqlite3` → `pg` (node-postgres)
5. **Async/Await:** All queries now use async/await pattern

## Benefits

✅ **Persistent data** - Survives code redeployments  
✅ **Multiple experiments** - Run new studies without losing old data  
✅ **Production-ready** - Railway/Render free tiers include managed Postgres  
✅ **Clean exports** - Export data per experiment  

## Database Schema

### New Tables:
- **`experiments`** - Track multiple studies over time
  - `id`, `name`, `description`, `status`, `created_at`, `completed_at`

### Updated Tables:
All data tables now include `experiment_id`:
- `participants`
- `annotations`
- `prompts`
- `task_assignments`
- `study_config`

### Default Data:
- **Experiment 1:** "Pilot Study - Format Comparison" (created automatically)
- Config copied from original schema

## Deployment Steps

### 1. Create PostgreSQL Database

**Railway:**
1. In your project, click "New" → "Database" → "Add PostgreSQL"
2. Railway will provision a Postgres instance
3. Copy the `DATABASE_URL` from the Variables tab

**Render:**
1. New → PostgreSQL
2. Name: `rlhf-pilot-db`
3. Free tier is fine
4. Copy the **Internal Database URL** after creation

### 2. Set Environment Variable

Add to your Railway/Render backend service:

```
DATABASE_URL=postgresql://username:password@host:port/database
```

Railway/Render will provide this automatically if you connect the database.

### 3. Initialize Database

The backend will auto-initialize on first run, or you can manually run:

```bash
npm run init-db
```

This creates all tables and inserts the default experiment + config.

### 4. Seed Example Prompts (Optional)

```bash
npm run seed-prompts
```

Adds 3 test prompts to the current active experiment.

### 5. Deploy

Push your code:

```bash
git add .
git commit -m "Migrate to PostgreSQL with experiment tracking"
git push
```

Railway/Render will auto-deploy.

## API Changes (Minimal)

All existing API endpoints work the same way. The only difference:

- Data is now scoped to the **current active experiment**
- Export endpoints include `experiment_id` in response

### Current Experiment

The system automatically uses the most recent `active` experiment:

```sql
SELECT id FROM experiments 
WHERE status = 'active' 
ORDER BY created_at DESC 
LIMIT 1
```

## Managing Multiple Experiments

### Create New Experiment

```sql
INSERT INTO experiments (name, description, status)
VALUES ('Pilot Study #2', 'Follow-up study with revised prompts', 'active');
```

### Mark Experiment Complete

```sql
UPDATE experiments 
SET status = 'completed', completed_at = NOW()
WHERE id = 1;
```

### Query Specific Experiment

```sql
SELECT * FROM annotations WHERE experiment_id = 1;
```

### Export by Experiment

```bash
# Via API
curl https://your-backend-url.railway.app/api/study/export/annotations

# Direct SQL
psql $DATABASE_URL -c "COPY (SELECT * FROM annotations WHERE experiment_id = 1) TO STDOUT CSV HEADER" > experiment1_annotations.csv
```

## Local Development

### 1. Install PostgreSQL locally

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu:**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create local database

```bash
psql postgres
CREATE DATABASE rlhf_pilot;
\q
```

### 3. Set environment variable

```bash
export DATABASE_URL="postgresql://localhost/rlhf_pilot"
```

Or add to `.env`:
```
DATABASE_URL=postgresql://localhost/rlhf_pilot
NODE_ENV=development
PORT=3001
```

### 4. Initialize & seed

```bash
cd backend
npm install
npm run init-db
npm run seed-prompts
npm start
```

## Troubleshooting

### "DATABASE_URL environment variable not set"
- Add `DATABASE_URL` to Railway/Render environment variables
- Format: `postgresql://user:password@host:port/database`

### "No active experiment found"
- Run `npm run init-db` to create default experiment
- Or manually insert experiment via SQL

### Connection refused
- Check PostgreSQL is running (local dev)
- Verify DATABASE_URL is correct
- Ensure SSL settings match environment (production uses SSL)

### SSL certificate error (production)
- Code uses `rejectUnauthorized: false` for Railway/Render free tiers
- If using custom Postgres, adjust SSL config in `db.js`

## Migration from Old SQLite Data (If Needed)

If you already collected data with SQLite and need to migrate:

1. **Export from SQLite:**
   ```bash
   sqlite3 data/pilot.db .dump > old_data.sql
   ```

2. **Convert to Postgres syntax** (handle differences like AUTOINCREMENT → SERIAL)

3. **Import into Postgres:**
   ```bash
   psql $DATABASE_URL < converted_data.sql
   ```

4. **Add experiment_id** to all rows:
   ```sql
   UPDATE participants SET experiment_id = 1;
   UPDATE annotations SET experiment_id = 1;
   -- etc.
   ```

For help with conversion, ask Scout!

## Summary

✅ **Migration complete** - Backend now uses PostgreSQL  
✅ **Experiment tracking added** - Multiple studies supported  
✅ **Production-ready** - Deploy to Railway/Render with managed Postgres  
✅ **Data persistent** - Survives redeployments  
✅ **API unchanged** - Frontend works without modification  

**Next:** Deploy to Railway/Render with PostgreSQL database!
