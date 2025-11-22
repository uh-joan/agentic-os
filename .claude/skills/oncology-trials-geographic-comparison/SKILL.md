---
name: get_oncology_trials_geographic_comparison
description: >
  Compare Phase 3 oncology trials recruiting in United States vs. China.
  Analyzes geographic distribution, therapeutic area trends, sponsor nationality,
  and strategic insights for expansion planning. Provides trial counts by country,
  top conditions, top sponsors, and cost-advantage analysis.

  Use this skill when:
  - Planning geographic expansion strategy
  - Selecting CRO partners for multi-regional trials
  - Analyzing competitive landscape by geography
  - Evaluating regulatory harmonization opportunities
  - Assessing cost advantages in Asian clinical development

  Keywords: geographic comparison, US vs China, oncology trials, Phase 3,
  recruiting status, CRO selection, expansion strategy, cost analysis,
  sponsor nationality, therapeutic area trends
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - multi_query_comparison
  - geographic_analysis
  - sponsor_analysis
data_scope:
  total_results: 518
  geographical: United States (339) vs China (179)
  temporal: Currently recruiting trials only
  phase: Phase 3
  therapeutic_area: Oncology (all cancer types)
created: 2025-11-22
last_updated: 2025-11-22
complexity: medium
execution_time: ~8 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_oncology_trials_geographic_comparison

## Purpose

Compare Phase 3 oncology trials currently recruiting in United States vs. China to inform geographic expansion strategy, CRO selection, and competitive positioning.

## Strategic Value

**Business Applications:**
- **Geographic Expansion**: Identify underserved therapeutic areas in each market
- **CRO Selection**: Evaluate competitive intensity by region
- **Cost Strategy**: Quantify enrollment advantages in China vs US
- **Regulatory Planning**: Assess dual-region trial feasibility
- **Partnership Decisions**: Identify dominant sponsors by geography

**Key Metrics:**
- Trial volume by country
- Therapeutic area distribution
- Sponsor nationality patterns
- Competitive intensity ratios

## Usage

### When to Use This Skill

Trigger this skill for queries about:
- "Compare oncology trials in US vs China"
- "Geographic distribution of Phase 3 cancer trials"
- "Where should we run our oncology trial - US or China?"
- "CRO selection for multi-regional oncology studies"
- "Cost advantages in Asian clinical trials"

### Command Line

```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/oncology-trials-geographic-comparison/scripts/get_oncology_trials_geographic_comparison.py
```

### Programmatic Import

```python
import sys
sys.path.insert(0, ".claude")
from skills.oncology_trials_geographic_comparison.scripts.get_oncology_trials_geographic_comparison import get_oncology_trials_geographic_comparison

result = get_oncology_trials_geographic_comparison()
print(f"US trials: {result['total_us']}")
print(f"China trials: {result['total_china']}")
```

## Implementation Details

### Data Collection Approach

**Dual Query Strategy:**
1. Query ClinicalTrials.gov for Phase 3 oncology trials in United States (RECRUITING)
2. Query ClinicalTrials.gov for Phase 3 oncology trials in China (RECRUITING)
3. Compare results across dimensions

**Pagination:**
- Uses token-based pagination to ensure complete datasets
- Processes up to 10 pages per query (safety limit)
- Typical execution: 2-3 pages per geography

**Response Format:**
- CT.gov returns markdown (not JSON)
- Regex-based parsing for trial fields
- Robust handling of optional fields

### Data Structure

```python
{
    'total_us': int,              # Count of US trials
    'total_china': int,           # Count of China trials
    'us_trials': [                # Full US trial details
        {
            'nct_id': str,
            'title': str,
            'status': str,
            'conditions': str,
            'sponsor': str,
            'interventions': str
        }
    ],
    'china_trials': [...],        # Full China trial details
    'us_top_conditions': [(condition, count)],
    'china_top_conditions': [(condition, count)],
    'us_top_sponsors': [(sponsor, count)],
    'china_top_sponsors': [(sponsor, count)],
    'summary': str                # Formatted comparison analysis
}
```

### Analysis Components

**Condition Analysis:**
- Parse and aggregate all conditions across trials
- Identify top 10 therapeutic areas per geography
- Compare priority areas between markets

**Sponsor Analysis:**
- Extract and categorize sponsor organizations
- Identify top 10 sponsors per geography
- Analyze sponsor nationality patterns

**Strategic Metrics:**
- Trial volume ratio (US:China)
- Competitive intensity comparison
- Cost advantage quantification
- Sponsor diversity assessment

## Output Format

### Summary Report

```
=== PHASE 3 ONCOLOGY TRIALS GEOGRAPHIC COMPARISON ===

OVERALL COMPARISON:
  United States: 339 recruiting trials
  China:         179 recruiting trials
  Ratio:         1.89:1 (US:China)

TOP CONDITIONS - UNITED STATES:
  • Non-Small Cell Lung Cancer: 31 trials
  • Breast Cancer: 28 trials
  [...]

TOP CONDITIONS - CHINA:
  • Non-Small Cell Lung Cancer: 19 trials
  • Solid Tumors: 15 trials
  [...]

STRATEGIC INSIGHTS:
  • Trial Volume: US dominates in Phase 3 oncology recruiting trials
  • Cost Advantage: China offers 47% fewer competing trials
  • Sponsor Mix: US has more diverse sponsors
  • CRO Strategy: Consider dual-region trials for regulatory harmonization
```

## Maintenance & Updates

**Data Freshness:**
- Data reflects live ClinicalTrials.gov status
- Query date included in output
- Re-run skill to get updated counts

**Known Limitations:**
- Only captures trials with location metadata
- Multi-national trials counted in both geographies
- Sponsor classification based on lead organization

**Future Enhancements:**
- Add European Union comparison
- Include trial start dates for trend analysis
- Classify sponsors by nationality (US vs Chinese companies)
- Add intervention type analysis (immunotherapy, targeted therapy, etc.)

## Version History

- **v1.0** (2025-11-22): Initial implementation with dual-query comparison
  - Pagination support for complete datasets
  - Condition and sponsor analysis
  - Strategic insights generation
