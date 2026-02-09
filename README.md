# RLHF Formats Comparison Pilot Study

**Optimizing Human Feedback Collection for RLHF through Experimental Validation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This platform enables controlled experiments comparing different elicitation formats for collecting human feedback on AI-generated responses. The pilot systematically tests three formats to identify the most efficient method for RLHF feedback collection.

### Formats Tested

1. **Pairwise Comparison** - Industry standard (Bradley-Terry model)
2. **Best-Worst Scaling** - MaxDiff method (proven 2-3× efficiency in other domains)
3. **Peer Prediction** - Bayesian Truth Serum (incentive-compatible without ground truth)

## Research Question

**Which feedback elicitation format maximizes information gain per annotation?**

### Key Metrics
- Information gain per annotation
- Inter-rater reliability  
- Time efficiency (info/minute)
- Cost efficiency (info/dollar)
- Cognitive load (inferred from timing + confidence)

## Features

### Backend (Node.js + Express + SQLite)
- ✅ RESTful API for participant management
- ✅ Automatic task randomization and balancing
- ✅ Support for within-subjects and between-subjects designs
- ✅ Real-time progress tracking
- ✅ Auto-generated completion codes
- ✅ Data export endpoints (JSON)
- ✅ Configurable study parameters

### Frontend (Static HTML/JS)
- ✅ Prolific integration (participant registration)
- ✅ Three annotation interfaces (Pairwise, BWS, Peer Prediction)
- ✅ Progress tracking with visual indicators
- ✅ Time tracking per annotation
- ✅ Confidence sliders for quality assessment
- ✅ Mobile-responsive design
- ✅ Clean, modern UI

## Quick Start

### Prerequisites
- Node.js v16+ and npm
- Python 3 (for local frontend serving) or any static file server

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/rlhf-formats-pilot.git
cd rlhf-formats-pilot
```

2. **Install backend dependencies**
```bash
cd backend
npm install
npm run init-db
npm run seed-prompts  # Optional: adds 3 example prompts
```

3. **Start backend**
```bash
npm run dev
# Backend runs on http://localhost:3001
```

4. **Serve frontend** (new terminal)
```bash
cd frontend
python3 -m http.server 8080
# Or: npx serve -p 8080
```

5. **Test locally**
```bash
# Visit: http://localhost:8080/?test=1
# test=1 bypasses Prolific ID requirement
```

## Project Structure

```
rlhf-formats-pilot/
├── backend/                 # Node.js/Express API
│   ├── src/
│   │   ├── models/         # Database schema
│   │   ├── routes/         # API endpoints
│   │   ├── utils/          # DB init, seed data
│   │   └── server.js       # Express app
│   └── package.json
│
├── frontend/               # Static HTML/JS/CSS
│   ├── index.html         # Landing page
│   ├── instructions.html  # Study instructions
│   ├── task-router.html   # Format routing
│   ├── completion.html    # Completion code
│   ├── shared/            # API client
│   ├── pairwise/          # Pairwise interface
│   ├── bws/               # BWS interface
│   └── peer-prediction/   # Peer Prediction interface
│
├── power_analysis*.py     # Statistical power simulations
├── *.png                  # Visualizations
├── DEPLOYMENT.md          # Deployment guide
└── PROJECT_README.md      # Full documentation
```

## Experimental Designs

### Within-Subjects (Recommended)
- Each participant uses all three formats
- 15-20 annotations per format (45-60 total)
- **Sample size:** 6-10 participants
- **Statistical power:** 80%+ for detecting 15-30% efficiency differences
- **Budget:** $600-800

### Between-Subjects
- Each participant uses one format only
- 15-20 annotations per participant
- **Sample size:** 30+ participants (10 per format)
- **Statistical power:** 65-70% for 30% difference
- **Budget:** $900-1,200

## Statistical Power

Validated through Monte Carlo simulations (10,000 iterations):

**Within-Subjects Design:**
- Conservative scenario (15% improvement): ~98% power
- Moderate scenario (30% improvement): ~100% power
- Optimistic scenario (50% improvement): ~100% power

See `power_curves_within_subjects.png` for visualizations.

## API Endpoints

### Participants
- `POST /api/participants/register` - Register via Prolific ID
- `GET /api/participants/:id/progress` - Get completion status
- `POST /api/participants/:id/complete` - Mark as completed

### Annotations
- `POST /api/annotations` - Submit annotation
- `GET /api/annotations/next/:participant_id` - Get next task

### Study Management
- `GET /api/study/config` - Get configuration
- `POST /api/study/config` - Update configuration
- `GET /api/study/stats` - Get study statistics
- `GET /api/study/export/:table` - Export data

See `backend/README.md` for full API documentation.

## Deployment

### Option 1: Railway + Vercel (Recommended)

**Backend (Railway):**
1. Connect GitHub repo to Railway
2. Auto-deploys on push
3. Set environment variables if needed

**Frontend (Vercel):**
1. Import project from GitHub
2. Set root directory to `frontend/`
3. Deploy

See `DEPLOYMENT.md` for detailed instructions.

### Option 2: Custom Hosting
- Backend: Any Node.js hosting (Heroku, DigitalOcean, AWS)
- Frontend: Any static hosting (Netlify, GitHub Pages, S3)

## Data Collection

### During Study
Monitor in real-time:
```bash
curl $API_URL/api/study/stats
```

### After Study
Export all data:
```bash
curl $API_URL/api/study/export/participants > participants.json
curl $API_URL/api/study/export/annotations > annotations.json
curl $API_URL/api/study/export/prompts > prompts.json
```

## Analysis

Data exports as JSON for easy import into R/Python/Stata:

```r
# R example
library(jsonlite)
annotations <- fromJSON("annotations.json")$data
participants <- fromJSON("participants.json")$data

# Calculate efficiency metrics
annotations %>%
  group_by(format) %>%
  summarize(
    avg_duration = mean(duration_ms),
    avg_confidence = mean(confidence, na.rm=TRUE)
  )
```

## Expected Outcomes

### Hypotheses
1. **BWS > Pairwise:** 2-3× information efficiency (validated in psychometrics, market research)
2. **Peer Prediction:** Unique insights without requiring ground truth
3. **Format × Task Type:** Interaction effects (some formats better for certain prompts)

### Efficiency Bounds
Estimated 15-50% cost savings vs. industry standard pairwise comparisons. At 100K annotation scale: **$15K-100K potential savings**.

## Budget

| Item | Cost |
|------|------|
| Infrastructure (Railway + Vercel) | $0-5/month |
| Participants - Within-subjects | $600-800 |
| Participants - Between-subjects | $900-1,200 |
| **Total (recommended)** | **~$600-850** |

## Timeline

- **Setup & Deploy:** 1 day
- **Optional Mini-Pilot:** 2-3 days ($150, 5 participants)
- **Full Study:** 3-5 days
- **Analysis:** 1-2 weeks
- **Total:** ~2-3 weeks end-to-end

## Contributing

This is a research project. If you'd like to collaborate or have questions, please open an issue or contact the research team.

## Citation

If you use this platform or methodology in your research, please cite:

```bibtex
@software{rlhf_formats_pilot_2026,
  author = {Sylvia, Sean},
  title = {RLHF Formats Comparison: Experimental Platform},
  year = {2026},
  url = {https://github.com/yourusername/rlhf-formats-pilot}
}
```

## License

MIT License - See LICENSE file for details

## Contact

- **Researcher:** Sean Sylvia
- **Institution:** UNC Chapel Hill, DHEPLab
- **Email:** [contact email]

## Acknowledgments

Theoretical framework draws from:
- Item Response Theory (psychometrics)
- Optimal Experimental Design (statistics)
- Mechanism Design (economics)
- Active Learning (machine learning)

---

**Last Updated:** 2026-02-09  
**Status:** Ready for deployment and testing
