---
name: get_companies_by_moa
description: >
  Comprehensive competitive query tool to identify companies working on specific mechanisms
  of action. Answers "Who's developing KRAS inhibitors?" with full trial analysis.

  Provides company breakdown with trial counts, development phases, drug names,
  and FDA approval status. Includes competitive assessment (leaders, late-stage,
  early-stage).

  Use when you need:
  - Quick competitive intelligence by mechanism
  - Company identification for partnerships/acquisitions
  - Development stage assessment (who's leading, who's early)
  - Competitive intensity check before starting program

  Trigger keywords: "companies working on", "who's developing", "competitive landscape",
  "mechanism of action", "MoA analysis", "company by mechanism"
category: competitive-intelligence
mcp_servers:
  - ct_gov_mcp
  - fda_mcp
patterns:
  - focused_query
  - company_attribution
  - competitive_assessment
  - moa_attribution
data_scope:
  total_results: Full analysis (all matching trials)
  geographical: Global
  temporal: Active trials only
created: 2025-11-25
last_updated: 2025-11-25
complexity: simple
execution_time: ~10-60 seconds (depends on trial count)
token_efficiency: ~99% reduction
test_config:
  args: ["KRAS inhibitor", "lung cancer"]
  expected_min_results: 3
  timeout_seconds: 90
---
# get_companies_by_moa


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What KRAS inhibitor drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved KRAS inhibitor medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for KRAS inhibitor`


## Purpose

Fast competitive query tool to answer "Who's working on [mechanism]?"

Focuses on:
- Company identification by mechanism of action
- Development stage assessment (Phase 1/2/3, approved)
- Competitive positioning (leaders vs followers)
- Quick screening for partnership/acquisition opportunities

## Usage

**Direct execution**:
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/companies-by-moa/scripts/get_companies_by_moa.py "KRAS inhibitor"

# With disease filter
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/companies-by-moa/scripts/get_companies_by_moa.py "PD-1 antibody" "melanoma"
```

**Import and use**:
```python
from skills.companies_by_moa.scripts.get_companies_by_moa import get_companies_by_moa

result = get_companies_by_moa("BTK inhibitor")
print(f"Total companies: {result['total_companies']}")
print(f"Leaders: {result['competitive_summary']['leaders']}")
```

## Parameters

- `moa` (required): Mechanism of action (e.g., "KRAS inhibitor", "GLP-1 agonist")
- `disease` (optional): Disease filter (e.g., "NSCLC", "diabetes")
- `phase_filter` (optional): Minimum phase (default: "Phase 1")
- `include_academic` (optional): Include academic sponsors (default: False)
- `sample_size` (optional): Number of trials to analyze (default: None = full analysis)

## Output Structure

Returns dict with:
- `moa`: Mechanism queried
- `disease`: Disease filter (if applied)
- `total_trials`: Total trials found by CT.gov query
- `sample_size`: Number of trials actually analyzed
- `analyzed_trials`: Trials with valid sponsor/drug data
- `total_companies`: Count of unique companies
- `companies`: Dict with company details:
  - `trials`: Trial count
  - `phases`: List of phases company is active in
  - `drugs`: List of drug names
  - `approved`: Count of approved drugs
  - `lead_phase`: Most advanced phase
- `competitive_summary`:
  - `leaders`: Companies with approved drugs
  - `late_stage`: Companies in Phase 3+
  - `early_stage`: Companies in Phase 1/2 only
  - `assessment`: Narrative competitive summary

## Example Output

```
COMPANY LANDSCAPE BY MECHANISM
================================================================================

📋 Mechanism: KRAS inhibitor
   Disease: Non-Small Cell Lung Cancer

📊 Overview:
   Total Companies: 6
   Total Trials: 23

🏢 Companies (sorted by development stage):

 1. Amgen                                  5 trials | 2 drugs
    Phases: Phase 1, Phase 2, Phase 3 (Lead: Phase 3) ✓ 1 approved
    Drugs: Sotorasib, AMG 510

 2. Bristol Myers Squibb                  3 trials | 1 drug
    Phases: Phase 2, Phase 3 (Lead: Phase 3) ✓ 1 approved
    Drugs: Adagrasib

 3. Revolution Medicines                  4 trials | 2 drugs
    Phases: Phase 1, Phase 2 (Lead: Phase 2)
    Drugs: RMC-6236, RMC-6291

================================================================================
COMPETITIVE ASSESSMENT
================================================================================

Established market with 2 approved drugs and active late-stage competition

✓ Market Leaders (2):
  - Amgen
  - Bristol Myers Squibb

⚡ Late-Stage Competitors (3):
  - Amgen
  - Bristol Myers Squibb
  - Eli Lilly

🔬 Early-Stage Explorers (3):
  - Revolution Medicines
  - Johnson & Johnson
  - Vividion Therapeutics
```

## When to Use This vs indication-drug-pipeline-breakdown

| Feature | This Skill (companies-by-moa) | pipeline-breakdown |
|---------|-------------------------------|-------------------|
| Query type | By mechanism of action | By indication (disease) |
| Focus | Companies and competitive positioning | Drugs and phase distribution |
| Coverage | Full analysis (all trials) | Full analysis with intelligent sampling |
| Example | "KRAS inhibitors" → Companies | "NSCLC" → All drugs/phases |
| Use case | Partnership screening | Pipeline strategy |

## Implementation Details

### Core Strategy

1. **Query CT.gov** for trials matching mechanism of action
2. **Extract sponsors** from trial data with M&A attribution
3. **Track per company**: trials, phases, drugs, lead phase
4. **Cross-check FDA** for approved drugs (sample for speed)
5. **Generate competitive summary** with strategic categories

### M&A Attribution

Reuses company hierarchy from `indication-drug-pipeline-breakdown`:
- Celgene → Bristol Myers Squibb
- Mirati Therapeutics → Bristol Myers Squibb
- Loxo Oncology → Eli Lilly
- Array BioPharma → Pfizer
- + 20 more mappings

### Academic Filtering

Optional removal of non-pharma sponsors using pattern matching:
- Universities, hospitals, medical centers
- Government institutions (NIH, NCI)
- Non-profit foundations

Default: `include_academic=False` (pharma-only focus)

## Limitations

1. **Performance**: Full analysis of large trial sets (>500 trials) takes 30-60 seconds
2. **MoA matching**: Text-based search (may miss synonyms)
3. **Academic filter**: Pattern-based (some edge cases)
4. **FDA API rate limits**: May slow down with very large drug lists (>100 unique drugs)

## Related Skills

- **indication-drug-pipeline-breakdown**: Complementary skill for disease-wide analysis
- **get_clinical_trials**: Basic trial search (no company tracking)
- **competitive-landscape-analyst**: Strategic agent using both skills

## Verification

Verified with:
- ✅ Execution: Clean exit, no errors
- ✅ Data retrieved: Company data extracted
- ✅ M&A attribution: Celgene → Bristol Myers Squibb working
- ✅ Executable: Standalone with `if __name__`
- ✅ Schema: Valid company structure