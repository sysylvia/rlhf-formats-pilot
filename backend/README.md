# RLHF Pilot Backend

Express API server for RLHF formats comparison pilot study.

## Quick Start

```bash
# Install dependencies
npm install

# Initialize database
npm run init-db

# Seed example prompts (optional, for testing)
npm run seed-prompts

# Start development server
npm run dev
```

Server runs on http://localhost:3000

## API Endpoints

### Health Check
- `GET /health` - Check server and database status

### Participants
- `POST /api/participants/register` - Register new participant from Prolific
  - Body: `{ prolific_pid: string }`
  - Returns: `{ participant_id, completion_code, format_assigned, design_type }`
  
- `POST /api/participants/:id/consent` - Record consent
- `POST /api/participants/:id/instructions` - Mark instructions as completed
- `POST /api/participants/:id/complete` - Mark participant as completed
- `GET /api/participants/:id/progress` - Get participant progress

### Annotations
- `POST /api/annotations` - Submit annotation
  - Body varies by format (see schema)
  
- `GET /api/annotations/next/:participant_id` - Get next task for participant
  - Returns: `{ done: boolean, task?: {...} }`

### Prompts (Admin)
- `GET /api/prompts` - Get all prompts
- `GET /api/prompts/:id` - Get single prompt
- `POST /api/prompts` - Add single prompt
- `POST /api/prompts/bulk` - Bulk add prompts

### Study (Admin)
- `GET /api/study/config` - Get study configuration
- `POST /api/study/config` - Update configuration
- `GET /api/study/stats` - Get study statistics
- `GET /api/study/export/:table` - Export table data (CSV)

## Study Configuration

Configure via `POST /api/study/config` or directly in database:

- `design_type`: `"within"` or `"between"`
- `annotations_per_format`: Number of annotations per format (default: 15)
- `formats_enabled`: Comma-separated formats (default: `"pairwise,bws,peer_prediction"`)
- `study_active`: `"1"` or `"0"`

## Database Schema

### Tables
- `participants` - Participant registration and metadata
- `prompts` - Annotation tasks (prompt + responses)
- `annotations` - Participant responses
- `task_assignments` - Task queue for within-subjects design
- `study_config` - Study configuration key-value store

See `src/models/schema.sql` for full schema.

## Development

```bash
# Watch mode (auto-restart on changes)
npm run dev

# Production mode
npm start
```

## Deployment

### Railway (Recommended)
1. Connect GitHub repo to Railway
2. Set environment variables (PORT handled automatically)
3. Deploy

### Docker
```bash
docker build -t rlhf-pilot-backend .
docker run -p 3000:3000 rlhf-pilot-backend
```

## Data Export

Export data for analysis:
```bash
curl http://localhost:3000/api/study/export/annotations > annotations.json
curl http://localhost:3000/api/study/export/participants > participants.json
```

## Notes

- SQLite database stored at `backend/data/pilot.db`
- Automatic task randomization and balancing
- Supports both within-subjects and between-subjects designs
- Completion codes auto-generated (format: RLHF2026-XXXXXXXX)
