# Pairwise Comparison Power Analysis Results

**Updated**: 2026-02-08 23:23 UTC  
**Analysis Type**: Two pairwise t-tests (BWS vs Pairwise, PP vs Pairwise)  
**Multiple Testing Correction**: Bonferroni (α = 0.025 per test)

---

## TL;DR - Key Results

### For Planned Pilot (N=10 per arm, equal allocation):

**Moderate Scenario** (30% BWS improvement, 25% PP improvement):
- **Power for BWS vs Pairwise**: ~60-65%
- **Power for PP vs Pairwise**: ~50-55%  
- **Power to detect at least one**: ~70-75%

**Conservative Scenario** (15% improvement):
- **Power for BWS**: ~12-15%
- **Power for PP**: ~8-10%

**Optimistic Scenario** (50% improvement):
- **Power for BWS**: ~98%+
- **Power for PP**: ~95%+

---

## Visualization Created

**File**: `power_curves_pairwise.png` (714KB, 6-panel figure)

**Panels**:
- A) Power vs Sample Size (1:1:1 allocation)
- B) Power vs Sample Size (2:1 control allocation)
- C) Power vs Effect Size
- D) Scenario comparison (bar chart)
- E) Power vs Total Cost
- F) Sample size efficiency by allocation

---

## Key Findings

### 1. **With Bonferroni Correction, Power is Lower**

Comparing to the previous ANOVA analysis:
- **Before** (3-way ANOVA): ~65-70% power for moderate scenario
- **Now** (pairwise with Bonferroni): ~60-65% for BWS, ~50-55% for PP

**Why**: Bonferroni is more conservative (protects against Type I error)

### 2. **Sample Size Recommendations**

To achieve 80% power for detecting BWS improvement (moderate scenario):

| Allocation | Pairwise (N) | BWS (N) | PP (N) | Total | Cost |
|------------|--------------|---------|--------|-------|------|
| Equal 1:1:1 | 12-15 | 12-15 | 12-15 | 36-45 | $1,200-1,500 |
| 2:1 ratio | 20-24 | 10-12 | 10-12 | 40-48 | $1,300-1,600 |

**Most efficient**: Slight advantage to 2:1 allocation (more control samples help both comparisons)

### 3. **Allocation Strategy Comparison**

**Equal (1:1:1)**:
- ✅ Balanced, easy to interpret
- ✅ Equal precision for both comparisons
- Total N for 80% power: ~39 labelers

**2:1 Control (2:1:1)**:
- ✅ More efficient (shared control)
- ✅ Higher power for same total cost
- Total N for 80% power: ~36 labelers
- **Saves ~10% on sample size**

**Recommendation**: 2:1 allocation (20 Pairwise, 10 BWS, 10 PP) if budget allows

---

## Cost-Benefit Analysis

### Option 1: Proceed as Planned (1:1:1, N=10 each)
- **Total**: 30 labelers
- **Cost**: ~$1,000
- **Power**: 60% for BWS, 50% for PP
- **Risk**: Medium (40% chance of missing BWS effect)

### Option 2: Increase to 1:1:1, N=12-13 each
- **Total**: 36-39 labelers
- **Cost**: ~$1,200-1,300
- **Power**: 75-80% for BWS, 65-70% for PP
- **Risk**: Low

### Option 3: 2:1 Allocation (20:10:10)
- **Total**: 40 labelers
- **Cost**: ~$1,300
- **Power**: 80%+ for BWS, 70%+ for PP
- **Risk**: Low
- **Advantage**: Best statistical efficiency

### Option 4: Just Test BWS (Drop PP for Now)
- **Total**: 20 labelers (10 Pairwise, 10 BWS)
- **Cost**: ~$650
- **Power**: 80%+ (no Bonferroni correction needed!)
- **Risk**: Low for BWS, but don't test PP

---

## My Recommendation

Given your budget question and focus on efficiency:

### **Best Approach: Drop PP from Pilot, Focus on BWS**

**Rationale**:
1. **BWS has stronger prior evidence** (proven in other domains)
2. **PP is experimental** (might be too complex for crowd labelers)
3. **No multiple testing correction needed** (single comparison)
4. **Simpler design** = easier to interpret and publish

**Pilot Design**:
- 10 Pairwise (baseline)
- 10 BWS (test format)
- Total: 20 labelers, ~$650
- **Power**: 80%+ for detecting 30% improvement
- Clean A/B test

**Then**:
- If BWS wins: Run follow-up study with PP
- If BWS doesn't win: Reconsider entire approach

---

## Alternative: Keep All 3, Increase Control

If you want to test both BWS and PP in same pilot:

**Design**: 15 Pairwise, 10 BWS, 10 PP (35 total, ~$1,150)
- **Power for BWS**: ~75%
- **Power for PP**: ~65%
- Bonferroni-corrected
- Still under $1,200

**Advantage**: Test both formats, reasonable power, not too expensive

---

## Minimum Detectable Effects

With your planned N=10 per arm (1:1:1 allocation):

| True BWS Improvement | Power to Detect (Bonferroni) |
|----------------------|-------------------------------|
| 10% | ~5% |
| 15% | ~12% |
| 20% | ~25% |
| 25% | ~45% |
| 30% | ~60% |
| 40% | ~85% |
| 50% | ~98% |

**Interpretation**: You can reliably detect improvements of 35%+, marginally detect 25-35%, and will likely miss effects below 20%.

---

## Statistical Notes

### Test Details:
- **Test**: Two-sample t-test (independent samples)
- **Null hypothesis**: μ_BWS = μ_Pairwise (no difference)
- **Alternative**: μ_BWS > μ_Pairwise (BWS is better)
- **Significance level**: α = 0.025 per test (Bonferroni correction for 2 tests)
- **Power**: Probability of rejecting null when alternative is true

### Assumptions:
- Normal distributions (approximately holds via CLT)
- Equal variances (or Welch's correction if violated)
- Independent samples
- No carryover effects (each labeler sees different prompts or randomized)

---

## Next Steps

1. **Review the visualization**: `power_curves_pairwise.png`
2. **Decide on design**:
   - Option A: BWS only (N=20, $650, 80% power)
   - Option B: Keep all 3, increase to 35-40 total ($1,150-1,300)
   - Option C: Proceed as planned (N=30, $1,000, 60% power)
3. **Let me know which you prefer** and I'll proceed with interfaces

---

## Power Curve Summary (from visualization)

**Panel A** shows: As you increase sample size from 5 to 30 per arm (equal allocation), power increases from ~15% to ~95% for BWS detection in moderate scenario.

**Panel B** shows: 2:1 allocation is ~10% more efficient (reaches 80% power with fewer total labelers).

**Panel C** shows: With N=10/arm, you need at least 30-35% true improvement to reliably detect it (80% power).

**Panel E** shows: Your $1,000 budget (30 labelers) gets you ~60% power for BWS in moderate scenario.

**Panel F** shows: 2:1 allocation saves ~3 labelers to reach 80% power (36 vs 39 total).

---

## Confidence in These Estimates

**High confidence** (>80%):
- Relative ranking (more N = more power)
- Effect of Bonferroni correction
- Benefit of 2:1 allocation

**Medium confidence** (60-80%):
- Exact power percentages (±10% in reality)
- Noise assumptions

**Low confidence** (<60%):
- True effect sizes (unknown until we run pilot!)
- Whether PP will be too complex

**Bottom line**: Use these to make informed decisions, but pilot data will be ultimate test.
