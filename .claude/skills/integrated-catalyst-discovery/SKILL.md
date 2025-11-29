---
title: Integrated Catalyst Discovery
description: End-to-end catalyst discovery combining bottom-up trial discovery with multi-source catalyst tracking
category: discovery
complexity: advanced
servers:
  - ct_gov_mcp
  - sec_edgar_mcp
  - financials_mcp
patterns:
  - integrated_workflow
  - enrichment_pattern
  - confidence_scoring
  - parameterized_by_time
therapeutic_area: generic
data_type: catalysts
version: 1.0.1
created: 2025-11-29
updated: 2025-11-29
bug_fixes:
  - Fixed dictionary key reference bug (line 98) - now correctly retrieves 'investable_companies' from discovery result
---

# Integrated Catalyst Discovery

Generic, end-to-end catalyst discovery for any quarter and year.

## Purpose

Combines two complementary approaches for comprehensive catalyst discovery:

1. **Bottom-Up Discovery** - Find companies with trials completing in target period
2. **Multi-Source Tracking** - Search for PDUFA dates, abstract acceptances, predictions
3. **Enrichment** - Add catalyst data to discovered companies
4. **Confidence Scoring** - Prioritize by HIGH/MEDIUM/LOW confidence

## Workflow

```
CT.gov Trials (Completing Q1 2026)
        ↓
Bottom-Up Discovery (36 companies, 80 trial events)
        ↓
Extract Company Names
        ↓
Multi-Source Tracking (PDUFA + Abstracts + Predictions)
        ↓
Enrichment (Add tracked catalysts to companies)
        ↓
Confidence Scoring:
  - HIGH: Has PDUFA date or abstract acceptance
  - MEDIUM: Has trial completions or predictions
  - LOW: Early stage only
        ↓
Sorted Results (HIGH → MEDIUM → LOW)
```

## Parameters

- `quarter`: Target quarter (Q1, Q2, Q3, Q4)
- `year`: Target year (e.g., 2025, 2026)
- `phases`: Trial phases (default: ['PHASE2', 'PHASE3'])
- `min_market_cap`: Minimum market cap filter (default: 0 = no filter)
- `max_discovery_trials`: Max trials to search (default: 5000)
- `max_tracking_companies`: Max companies to track with SEC (default: 100)
- `include_predicted`: Include trial predictions (default: True)
- `min_prediction_probability`: Min probability for predictions (default: 0.6)

## Usage

### Command Line (Any Quarter/Year)

```bash
# Q1 2026
PYTHONPATH=.claude:$PYTHONPATH python3 \
  .claude/skills/integrated-catalyst-discovery/scripts/discover_catalysts.py

# Edit script to change quarter/year parameters
```

### Python Import

```python
from integrated_catalyst_discovery.scripts.discover_catalysts import discover_catalysts

# Discover Q4 2025 catalysts
result = discover_catalysts(
    quarter="Q4",
    year=2025,
    phases=['PHASE2', 'PHASE3'],
    min_market_cap=0,  # No filter
    max_tracking_companies=50
)

print(f"Total companies: {result['total_companies']}")
print(f"Confidence breakdown: {result['confidence_breakdown']}")

# Access companies by confidence
for company in result['companies']:
    if company['confidence'] == 'HIGH':
        print(f"{company['name']}: {len(company['tracked_catalysts'])} catalysts")
```

## Returns

```python
{
    'quarter': 'Q1 2026',
    'total_companies': 36,
    'companies': [
        {
            'name': 'Pfizer Inc',
            'ticker': 'PFE',
            'market_cap': 150000000000,
            'trials': [...],  # Trial completion events
            'tracked_catalysts': [...],  # PDUFA/abstracts/predictions
            'confidence': 'HIGH',  # HIGH/MEDIUM/LOW
            'phase_breakdown': {...}
        },
        ...
    ],
    'discovery_stats': {...},
    'tracking_stats': {...},
    'confidence_breakdown': {
        'HIGH': 5,
        'MEDIUM': 20,
        'LOW': 11
    },
    'total_trial_events': 80,
    'total_tracked_catalysts': 12
}
```

## Confidence Levels

- **HIGH**: Has dated catalysts (PDUFA dates, abstract acceptances)
  - Actionable, specific dates
  - Highest priority for tracking

- **MEDIUM**: Has trial completions or predictions
  - Trial completing in target period
  - Predicted conference presentations
  - Medium priority

- **LOW**: Early stage or no specific catalyst
  - Phase 1 trials
  - No confirmed events
  - Lowest priority

## Key Features

✅ **Generic** - Works for any quarter/year (Q1 2026, Q4 2025, etc.)

✅ **Comprehensive** - Combines trial completions + regulatory + conference catalysts

✅ **Enrichment Pattern** - Keeps ALL companies, prioritizes by confidence

✅ **No Filtering** - Default min_market_cap = 0 (user requested)

✅ **Rate Limited** - SEC tracking limited to prevent rate limiting

✅ **Sorted Output** - HIGH confidence first, then MEDIUM, then LOW

## Example Output

```
INTEGRATED CATALYST DISCOVERY: Q1 2026
================================================================================

🔍 STEP 1: BOTTOM-UP DISCOVERY
Target: Q1 2026
Phases: PHASE2, PHASE3
✓ Discovery complete
  Companies found: 36
  Catalyst events: 80

📊 STEP 2: CATALYST TRACKING
Tracking 36 companies
✓ Tracking complete
  Additional catalysts found: 8
  Sources: {'PREDICTION': 8}

💎 STEP 3: ENRICHMENT
✓ Enrichment complete
  Companies with tracked catalysts: 6

🎯 STEP 4: CONFIDENCE SCORING
✓ Confidence scoring complete
  HIGH confidence: 2 companies
  MEDIUM confidence: 25 companies
  LOW confidence: 9 companies
```

## Notes

- PDUFA and abstract trackers typically return 0 (companies don't file 8-Ks)
- Trial completion predictor provides majority of tracked catalysts
- All companies retained regardless of catalyst availability
- Enrichment pattern requested by user (vs filtering pattern)
