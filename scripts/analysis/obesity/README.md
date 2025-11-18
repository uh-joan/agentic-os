# Obesity Clinical Trials Pipeline Analysis

Comprehensive pipeline analysis scripts for obesity clinical trials in the United States.

## Scripts

### 1. `obesity_pipeline_analysis.py`
**Full pipeline analysis across all trial statuses**

Analyzes:
- Total obesity trials (5,665 trials)
- Phase distribution (Early Phase 1 through Phase 4)
- Trial status (recruiting, active, completed, not yet recruiting)
- Sponsor types (industry vs academic)
- Key drug classes (GLP-1, Semaglutide, Tirzepatide, etc.)
- Strategic insights

**Usage:**
```bash
python3 scripts/analysis/obesity/obesity_pipeline_analysis.py
```

**Key Findings:**
- 5,665 total obesity trials in US
- 653 actively recruiting (11.5%)
- 313 Phase 3 trials (5.5%)
- 231 GLP-1 trials (4.1%)
- HIGH market maturity, INTENSE competition

### 2. `obesity_active_pipeline_analysis.py`
**Active trials only (recruiting + active not recruiting)**

Focuses on:
- Currently active competitive landscape
- 968 active trials (653 recruiting + 315 active not recruiting)
- Active trials by phase (47 Phase 3, 84 Phase 2)
- Industry vs academic activity in active trials
- GLP-1 dominance in active trials (52 active)
- Competitive intensity scoring
- Near-term pipeline velocity

**Usage:**
```bash
python3 scripts/analysis/obesity/obesity_active_pipeline_analysis.py
```

**Key Findings:**
- 968 active trials (653 recruiting, 315 active not recruiting)
- 47 active Phase 3 trials (near-term threats, 1-3 year readouts)
- 52 active GLP-1 trials (5.4% of active trials)
- Competitive Intensity Score: 705/1000 - EXTREMELY INTENSE
- 653 trials competing for patients RIGHT NOW

## Output Structure

Both scripts generate structured analysis:

```
====================================================================================================
[TITLE]
====================================================================================================

[Data Collection Phase - 6-7 phases]
[1/6] Gathering data...
[2/6] Analyzing by phase...
...

====================================================================================================
ANALYSIS RESULTS
====================================================================================================

1. [LANDSCAPE OVERVIEW]
2. [PHASE DISTRIBUTION]
3. [STATUS/SPONSOR DISTRIBUTION]
4. [KEY DRUG CLASSES]

====================================================================================================
STRATEGIC INSIGHTS
====================================================================================================

• Market Maturity
• Current Competition
• Industry Activity
• GLP-1 Dominance
• Pipeline Velocity
• Competitive Intensity Score

====================================================================================================
KEY TAKEAWAYS FOR COMPETITIVE STRATEGY
====================================================================================================

1. Patient Enrollment Competition
2. GLP-1 Market Saturation
3. Industry Focus
4. Phase 3 Near-Term Competition

====================================================================================================
ANALYSIS COMPLETE
====================================================================================================
```

## Saving Results

**Create dated output directory:**
```bash
mkdir -p data_dump/$(date +%Y-%m-%d)_obesity_pipeline
```

**Save all trials analysis:**
```bash
python3 scripts/analysis/obesity/obesity_pipeline_analysis.py > \
  data_dump/$(date +%Y-%m-%d)_obesity_pipeline/all_trials.txt
```

**Save active trials analysis:**
```bash
python3 scripts/analysis/obesity/obesity_active_pipeline_analysis.py > \
  data_dump/$(date +%Y-%m-%d)_obesity_pipeline/active_trials.txt
```

**Run both and save:**
```bash
mkdir -p data_dump/$(date +%Y-%m-%d)_obesity_pipeline
python3 scripts/analysis/obesity/obesity_pipeline_analysis.py > \
  data_dump/$(date +%Y-%m-%d)_obesity_pipeline/all_trials.txt 2>&1
python3 scripts/analysis/obesity/obesity_active_pipeline_analysis.py > \
  data_dump/$(date +%Y-%m-%d)_obesity_pipeline/active_trials.txt 2>&1
echo "Analysis complete. Results saved to data_dump/$(date +%Y-%m-%d)_obesity_pipeline/"
```

## Key Metrics Comparison

| Metric | All Trials | Active Trials Only |
|--------|-----------|-------------------|
| **Total Trials** | 5,665 | 968 (653 recruiting + 315 active) |
| **Phase 3** | 313 (5.5%) | 47 (4.9% of active) |
| **Phase 2** | 575 (10.2%) | 84 (8.7% of active) |
| **Industry Sponsored** | 773 (13.6%) | 653 (67.5% of active) |
| **GLP-1 Trials** | 231 (4.1%) | 52 (5.4% of active) |
| **Semaglutide** | 118 | 38 |
| **Tirzepatide** | 85 | 30 |

## Strategic Insights

### All Trials Analysis
- **Market Maturity:** HIGH (313 Phase 3 trials total)
- **Competition:** INTENSE (653 recruiting)
- **GLP-1 Dominance:** VERY HIGH (231 trials, 4.1%)
- **Semaglutide Leadership:** 118 trials (market leader)

### Active Trials Analysis
- **Current Competition:** EXTREMELY INTENSE (653 recruiting NOW)
- **Patient Enrollment:** Critical bottleneck
- **Phase 3 Pipeline:** 47 trials (near-term 1-3 year readouts)
- **Competitive Intensity:** 705/1000 - Saturated market
- **Industry Confidence:** HIGH (67.5% of active trials)

## Use Cases

### Competitive Intelligence
Use `obesity_active_pipeline_analysis.py` to:
- Identify near-term competitive threats (47 Phase 3 trials)
- Assess patient enrollment competition (653 recruiting trials)
- Evaluate GLP-1 market saturation (52 active GLP-1 trials)
- Track industry confidence (67.5% industry-sponsored active trials)

### Market Assessment
Use `obesity_pipeline_analysis.py` to:
- Understand overall market size (5,665 trials)
- Assess historical development activity (3,815 completed)
- Evaluate mechanism diversity (GLP-1 vs alternatives)
- Benchmark against total market opportunity

### Strategic Planning
Combine both analyses to:
- Identify white space opportunities (alternative mechanisms)
- Assess differentiation requirements (GLP-1 saturation)
- Evaluate partnership opportunities (industry vs academic split)
- Plan trial enrollment strategies (competitive intensity)

## Technical Details

### MCP Queries Used

1. **Base Query:**
   ```python
   search(condition='obesity', location='United States', pageSize=10)
   ```

2. **Phase Filter:**
   ```python
   search(condition='obesity', phase='PHASE3', location='United States', pageSize=10)
   ```

3. **Status Filter:**
   ```python
   search(condition='obesity', status='recruiting', location='United States', pageSize=10)
   ```

4. **Intervention Filter:**
   ```python
   search(condition='obesity', intervention='semaglutide', location='United States', pageSize=10)
   ```

5. **Combined Filters (Active Trials):**
   ```python
   search(condition='obesity', status='recruiting OR active_not_recruiting',
          phase='PHASE3', location='United States', pageSize=10)
   ```

### Count Extraction

Regex pattern handles comma-formatted numbers:
```python
def extract_count(text):
    match = re.search(r'(\d+) of ([\d,]+) studies found', text)
    return int(match.group(2).replace(',', '')) if match else 0
```

### Execution Time

- **All Trials:** ~30-40 seconds (7 queries)
- **Active Trials:** ~40-50 seconds (12 queries with combined filters)

## Next Steps

Potential enhancements:
1. Add geographic breakdown (states, regions)
2. Include enrollment velocity analysis
3. Add sponsor-specific deep dives (top 10 sponsors)
4. Temporal analysis (trials by year)
5. Endpoint analysis (primary endpoints)
6. Biomarker integration (patient populations)
