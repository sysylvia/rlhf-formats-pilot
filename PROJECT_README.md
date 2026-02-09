# RLHF Formats Comparison Pilot Study

## Overview

This platform enables controlled experiments comparing different elicitation formats for collecting human feedback on AI-generated responses. The pilot tests three formats:

1. **Pairwise Comparison** (Industry standard - Bradley-Terry model)
2. **Best-Worst Scaling** (MaxDiff - proven 2-3× efficiency in other domains)
3. **Peer Prediction** (Bayesian Truth Serum - incentive-compatible without ground truth)

## Research Question

**Which feedback elicitation format is most efficient for RLHF?**

Metrics:
- Information gain per annotation
- Inter-rater reliability
- Time per annotation
- Cognitive load (inferred from timing + confidence)

## Experimental Designs

### Within-Subjects (Recommended)
- Each labeler uses all three formats
- 15-20 annotations per format (45-60 total per labeler)
- 6-10 labelers needed for 80%+ statistical power
- **Cost:** $600-800

**Advantages:**
- 7-8× more statistical power (controls for individual differences)
- More robust to outliers
- Can analyze format preferences per person

### Between-Subjects
- Each labeler uses one format only
- 15-20 annotations per labeler
- 30+ labelers needed (10+ per format)
- **Cost:** $900-1,200

**Advantages:**
- No order effects
- Simpler design
- Easier to scale

## Project Structure

```
rlhf-formats-pilot/
├── backend/                 # Node.js/Express API
│   ├── src/
│   │   ├── models/         # Database schema
│   │   ├── routes/         # API endpoints
│   │   └── utils/          # DB initialization, seed data
│   ├── data/               # SQLite database (generated)
│   └── package.json
│
├── frontend/               # Static HTML/JS/CSS
│   ├── index.html         # Landing page
│   ├── instructions.html  # Study instructions
│   ├── task-router.html   # Routes to correct format
│   ├── completion.html    # Completion code display
│   ├── shared/            # Shared API client
│   ├── pairwise/          # Pairwise interface
│   ├── bws/               # Best-Worst Scaling interface
│   └── peer-prediction/   # Peer Prediction interface
│
├── power_analysis*.py     # Statistical power simulations
├── *.png                  # Power analysis visualizations
└── *.md                   # Documentation

```

## Quick Start

### 1. Install Backend
```bash
cd backend
npm install
npm run init-db
npm run seed-prompts  # Optional: test prompts
```

### 2. Start Backend
```bash
npm run dev  # Development mode
# Backend runs on http://localhost:3000
```

### 3. Serve Frontend
```bash
cd frontend
python3 -m http.server 8080
# Or: npx serve
# Frontend available at http://localhost:8080
```

### 4. Test Locally
Visit: `http://localhost:8080/?test=1`
- `test=1` bypasses Prolific ID check
- Complete full flow to verify everything works

## Key Features

### Backend
- ✅ Automatic participant registration via Prolific ID
- ✅ Task randomization and balancing
- ✅ Support for both within/between-subjects designs
- ✅ Real-time progress tracking
- ✅ Auto-generated completion codes
- ✅ Data export endpoints (JSON)
- ✅ Study configuration API

### Frontend
- ✅ Mobile-responsive (desktop recommended)
- ✅ Progress bars
- ✅ Time tracking per annotation
- ✅ Confidence sliders
- ✅ Clean, modern UI with gradients
- ✅ Error handling and validation

### Data Collected Per Annotation
- Participant ID (Prolific PID)
- Prompt ID
- Format used
- Choice/rating (format-specific)
- Confidence level (0-100%)
- Duration (milliseconds)
- Order shown (1st, 2nd, 3rd annotation)
- Response order (for randomization tracking)

## Statistical Power

### Within-Subjects Design (Recommended)
**Sample size:** 6-10 labelers × 45-60 annotations

| Scenario | Effect Size | Power |
|----------|-------------|-------|
| Conservative | 15% improvement | ~98% |
| Moderate | 30% improvement | ~100% |
| Optimistic | 50% improvement | ~100% |

**Visualizations:** `power_curves_within_subjects.png`

### Between-Subjects Design
**Sample size:** 30 labelers (10 per format) × 15-20 annotations

| Scenario | Effect Size | Power |
|----------|-------------|-------|
| Conservative | 15% improvement | ~17% |
| Moderate | 30% improvement | ~65-70% |
| Optimistic | 50% improvement | ~100% |

**Visualizations:** `power_curves_pairwise.png`

## Expected Outcomes

### Primary Metrics
1. **Information gain:** Bits of information per annotation
2. **Time efficiency:** Information per minute
3. **Cost efficiency:** Information per dollar

### Secondary Metrics
1. **Inter-rater reliability:** Agreement between labelers
2. **Confidence:** Self-reported certainty
3. **Completion rate:** Drop-off analysis

### Hypotheses
1. **BWS > Pairwise:** 2-3× information efficiency (validated in other domains)
2. **Peer Prediction:** Unique insights without ground truth
3. **Format × Task Type interaction:** Some formats better for certain prompt types

## Analysis Plan

### Data Processing
```r
# Load data
participants <- read_json("participants.json")
annotations <- read_json("annotations.json")

# Calculate metrics per format
efficiency <- annotations %>%
  group_by(format) %>%
  summarize(
    avg_duration = mean(duration_ms),
    avg_confidence = mean(confidence),
    n_annotations = n()
  )
```

### Statistical Tests
1. **Repeated measures ANOVA** (within-subjects)
2. **Pairwise comparisons** with Bonferroni correction
3. **Mixed-effects models** (account for prompt difficulty, labeler expertise)

### Visualizations
- Information gain per format (boxplots)
- Time distributions (violin plots)
- Confidence × format (scatter)
- Learning curves (time vs order_shown)

## Deployment

See **DEPLOYMENT.md** for full instructions.

**Quick deploy:**
1. Backend → Railway (auto-deploy from Git)
2. Frontend → Vercel (static hosting)
3. Connect via Prolific

## Data Management

### During Study
- Real-time monitoring via `/api/study/stats`
- Automatic data persistence (SQLite)
- No manual intervention needed

### Post-Study
```bash
# Export all data
curl $API_URL/api/study/export/participants > data/participants.json
curl $API_URL/api/study/export/annotations > data/annotations.json
curl $API_URL/api/study/export/prompts > data/prompts.json
```

### Analysis
- Import JSON into R/Python/Stata
- Use `participant_id` to link across tables
- Merge with `prompts` for prompt text

## Budget

| Item | Cost |
|------|------|
| **Infrastructure** | |
| Railway (backend) | $0-5/month |
| Vercel (frontend) | $0 |
| **Participants (Within-Subjects)** | |
| 6-10 labelers × 45-60 annotations | $600-800 |
| **Participants (Between-Subjects)** | |
| 30 labelers × 15-20 annotations | $900-1,200 |
| **Total (Within)** | ~$600-850 |
| **Total (Between)** | ~$900-1,250 |

## Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Setup | 1 day | Deploy, test, load prompts |
| Pilot (optional) | 2-3 days | 5 labelers, $150, validate |
| Full study | 3-5 days | Recruit, run, monitor |
| Data export | 1 hour | Download, backup |
| Analysis | 1-2 weeks | Clean, analyze, visualize |
| **Total** | ~2-3 weeks | End-to-end |

## Next Steps

1. **Load Prompts:** Populate database with 100+ real prompts (currently has 3 examples)
2. **IRB Approval:** Submit protocol if required by institution
3. **Deploy:** Push to Railway + Vercel
4. **Test:** Run through full flow with test participants
5. **Launch:** Create Prolific study and recruit
6. **Monitor:** Check stats endpoint during study
7. **Export & Analyze:** Download data and run analysis scripts

## References

- **Power Analysis:** `PAIRWISE_POWER_RESULTS.md`, `power_curves_*.png`
- **Deployment:** `DEPLOYMENT.md`
- **Backend API:** `backend/README.md`
- **Theoretical Framework:** Google Drive folder (literature review, format taxonomy)

## Contact

- **Researcher:** Sean Sylvia
- **Institution:** UNC Chapel Hill, DHEPLab
- **Project:** RLHF Formats Comparison

---

**Last Updated:** 2026-02-09  
**Version:** 1.0.0  
**Status:** Ready for deployment and testing
