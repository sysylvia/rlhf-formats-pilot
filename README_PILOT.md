# RLHF Elicitation Formats Pilot - Ready to Launch! 🚀

**Status**: ✅ **ALL SYSTEMS READY**  
**Date**: 2026-02-09  
**Design**: Within-Subjects (8 labelers, 15 annotations each)

---

## 📋 **What's Been Built**

### ✅ **Power Analysis Complete**
- Monte Carlo simulations (10K+ runs)
- Three design types tested (between-subjects, pairwise, within-subjects)
- **Result**: Within-subjects gives **~7-8× more power** than between-subjects!
- **Power for recommended design**: ≥99% for BWS, ≥94% for PP

### ✅ **All 3 Annotation Interfaces Built**
1. **`interface_pairwise.html`** - Pairwise comparison (baseline)
2. **`interface_bws.html`** - Best-Worst Scaling
3. **`interface_peer_prediction.html`** - Peer Prediction with incentives

### ✅ **Experiment Coordinator**
- **`experiment_coordinator.py`** - Full counterbalancing logic
- Generates labeler sequences automatically
- Creates data collection templates
- Manages randomization

### ✅ **Experiment Data Ready**
- **`experiment_data/`** - All experimental materials
  - 8 labeler sequences (JSON files)
  - Counterbalancing scheme
  - 144 placeholder prompts (ready to replace with real data)
  - Data collection CSV template

---

## 🎯 **Recommended Design**

### **Sample Size**: 8 labelers

### **Design**: Within-subjects (repeated measures)
- Each labeler completes **15 annotations** (5 per format)
- Format order **counterbalanced** across labelers
- Each prompt seen by labeler in **ONE format only** (no repetition)

### **Power**:
- BWS vs Pairwise: **≥99%**
- PP vs Pairwise: **≥94%**
- Bonferroni-corrected for 2 comparisons

### **Cost**: ~$500
- 8 labelers × ~1 hour × $15/hr × ~1.4 (with bonuses & fees)

### **Timeline**: 
- Setup: 2 days
- Data collection: 1 week
- Analysis: 3-4 days

---

## 📁 **File Structure**

```
rlhf-formats-pilot/
├── README_PILOT.md                           ← You are here
├── power_analysis_within_subjects.py         ← Power simulations
├── power_curves_within_subjects.png          ← Visualization (506KB)
├── WITHIN_SUBJECTS_RESULTS.md                ← Detailed results
│
├── interface_pairwise.html                   ← Pairwise interface ✅
├── interface_bws.html                        ← BWS interface ✅
├── interface_peer_prediction.html            ← PP interface ✅
│
├── experiment_coordinator.py                 ← Setup script ✅
├── prompts.json                              ← Placeholder prompts (144)
│
└── experiment_data/
    ├── experiment_summary.txt                ← Counterbalancing plan
    ├── annotation_data_template.csv          ← Data collection template
    └── labeler_sequences/
        ├── labeler_01_sequence.json          ← Labeler 1's tasks
        ├── labeler_02_sequence.json          ← Labeler 2's tasks
        └── ... (8 total)
```

---

## 🚀 **Next Steps to Launch**

### **1. Prepare Real Prompts** (1-2 hours)

Replace `prompts.json` with real RLHF prompts. Format:

```json
[
  {
    "id": "prompt_001",
    "text": "Your actual prompt here",
    "responses": {
      "A": "Response A text",
      "B": "Response B text",
      "C": "Response C text",
      "D": "Response D text"
    },
    "metadata": {
      "source": "HH-RLHF",
      "difficulty": "medium"
    }
  },
  ...
]
```

**Source**: Use HH-RLHF dataset or generate with GPT-4.

**How many needed**: 120 prompts minimum (144 recommended with buffer).

---

### **2. Deploy Interfaces** (2-4 hours)

**Option A: Simple (for mini-pilot)**
- Host HTML files on local server or GitHub Pages
- Load sequences manually for each labeler

**Option B: Production (for full pilot)**
- Set up backend (Flask/FastAPI)
- API endpoints:
  - `GET /sequence/<labeler_id>` → Returns labeler's sequence
  - `POST /submit` → Saves annotation data
- Deploy on Heroku/Vercel/Railway (free tier OK)

**Option C: Platform Integration**
- Embed in Prolific/MTurk as external survey
- Pass labeler ID as URL parameter
- Return data via webhook

---

### **3. Mini-Pilot** (1 day, optional but recommended)

**Goal**: Test interfaces with 2-3 people before full launch

**Protocol**:
1. You + 2 colleagues each complete 1 sequence (15 annotations)
2. Time yourselves
3. Note any confusions, bugs, UX issues
4. Collect feedback on:
   - Were instructions clear?
   - Was Peer Prediction too confusing?
   - Any technical issues?

**Iterate**: Fix issues before full launch

---

### **4. Full Pilot Launch** (1 week)

**Recruitment** (via Prolific recommended):
- 8 labelers
- Requirements:
  - Native English speakers
  - 95%+ approval rate
  - 100+ prior tasks
- Payment: $15/hr + quality bonuses
- Est. time: 1 hour per labeler

**Quality Control**:
- Attention checks (1 per 5 annotations)
- Break reminders (after each format block)
- Monitor data quality in real-time
- Flag/replace labelers with <80% attention check pass rate

**Data Collection**:
- Responses saved to CSV
- Timestamps recorded
- Format order tracked
- Metadata preserved

---

### **5. Analysis** (3-4 days)

**Primary Analysis**:
1. **Paired t-tests**:
   - BWS vs Pairwise (Bonferroni α = 0.025)
   - PP vs Pairwise (Bonferroni α = 0.025)

2. **Effect sizes**:
   - Cohen's d for paired samples
   - Mean differences with 95% CI

3. **Power check**:
   - Did we achieve expected power?
   - Sensitivity analysis

**Secondary Analysis**:
4. **Order effects**: ANOVA with format order as factor
5. **Learning curves**: Accuracy vs annotation number
6. **Individual differences**: Which labelers preferred which formats?

**Visualization**:
- Box plots of accuracy by format
- Individual trajectories (spaghetti plot)
- Effect size forest plot

**Write-up**:
- Methods section (pre-register on OSF?)
- Results table
- Discussion of implications
- arXiv preprint

---

## 🔍 **Troubleshooting**

### **Problem**: Labelers confused by Peer Prediction

**Solution**:
- Add tutorial mode (3 practice examples with feedback)
- Simplify explanation
- Consider dropping PP if >30% of labelers fail attention checks

---

### **Problem**: Fatigue effects (quality drops after 10+ annotations)

**Solution**:
- Enforce breaks (5 min after each format block)
- Reduce to 4 prompts/format instead of 5
- Analyze first 10 vs last 5 annotations separately

---

### **Problem**: Low inter-rater reliability

**Solution**:
- Check if prompts are too ambiguous
- Add qualification test before main task
- Recruit higher-quality labelers (expert panel instead of crowd)

---

### **Problem**: Power is lower than expected

**Solution**:
- Recruit 2-3 more labelers (N=10-11 total)
- Extend to 6 prompts/format
- Focus analysis on BWS only (drop PP to avoid Bonferroni penalty)

---

## 📊 **Expected Results**

Based on power analysis (moderate scenario: 30% BWS improvement):

### **Primary Outcomes**:
- **BWS vs Pairwise**: p < 0.001, d ≈ 0.85, 30% improvement detected
- **PP vs Pairwise**: p < 0.01, d ≈ 0.65, 25% improvement detected

### **Secondary Findings**:
- Small learning effect (~2% improvement over 15 annotations)
- Minimal order effects (format order doesn't matter after randomization)
- Individual differences: Some labelers prefer BWS, others PP

### **Implications**:
- BWS is significantly more efficient than standard pairwise
- Could reduce RLHF annotation costs by 20-35%
- At scale (100K annotations): $20K-35K savings
- PP shows promise but needs more investigation

---

## 📄 **Data Dictionary**

### **annotation_data_template.csv**:

| Field | Type | Description |
|-------|------|-------------|
| `labeler_id` | int | Labeler identifier (1-8) |
| `annotation_number` | int | Annotation sequence number (1-15) |
| `format` | string | pairwise, bws, or peer_prediction |
| `prompt_id` | string | Prompt identifier |
| `choice` | string | Selected response (A/B for pairwise/PP, best/worst for BWS) |
| `prediction_pct` | int | PP only: predicted % choosing A (0-100) |
| `confidence` | int | Confidence rating (1-5) |
| `time_seconds` | int | Time spent on annotation |
| `timestamp` | ISO8601 | When submitted |
| `notes` | string | Any notes or issues |

---

## 🎓 **Academic Precedent**

This design follows best practices from:

1. **Psychometrics**: Within-subjects for test comparison (Nunnally & Bernstein, 1994)
2. **UX Research**: Counterbalanced usability testing (Nielsen, 2000)
3. **Preference Learning**: Paired comparison experiments (Thurstone, 1927)
4. **RLHF**: Standard annotation practices (Christiano et al., 2017)

**Novel contribution**: First systematic comparison of elicitation formats in RLHF context.

---

## ✅ **Pre-Launch Checklist**

- [ ] Real RLHF prompts loaded into `prompts.json`
- [ ] All 3 interfaces tested in browser
- [ ] Backend deployed (if using Option B)
- [ ] Prolific study created
- [ ] Mini-pilot completed with 2-3 people
- [ ] Issues from mini-pilot fixed
- [ ] Attention checks working
- [ ] Data logging verified
- [ ] IRB approval (if required by institution)
- [ ] Pre-registration (OSF recommended)

---

## 💡 **Tips for Success**

1. **Test everything twice** before launch (Murphy's Law!)
2. **Monitor first 2-3 labelers** closely (catch issues early)
3. **Have backup plan** for PP if it's too confusing
4. **Communicate clearly** in instructions (pilot test on non-experts)
5. **Log everything** (you'll want extra metadata later)
6. **Be responsive** if labelers have questions
7. **Celebrate milestones** (first labeler, halfway point, completion!)

---

## 🎯 **Success Criteria**

### **Minimum Viable Result**:
- ✅ Detect BWS improvement (p < 0.05)
- ✅ Reasonable data quality (>80% attention checks passed)
- ✅ Publishable findings (arXiv at minimum)

### **Strong Result**:
- ✅ Both BWS and PP show improvements
- ✅ Effect sizes align with predictions (d > 0.5)
- ✅ No major order effects or quality issues
- ✅ Conference paper quality (NeurIPS workshop)

### **Exceptional Result**:
- ✅ Very large effects (>30% improvement)
- ✅ Clear format × prompt interactions discovered
- ✅ Generalizable findings across prompt types
- ✅ Full conference paper (ICML/NeurIPS)

---

## 📞 **Support**

Questions? Issues? Contact Scout (that's me!). I built this, so I can help debug.

**Good luck! This is going to be great.** 🚀

---

**Last Updated**: 2026-02-09 01:00 UTC  
**Status**: Ready for mini-pilot launch
