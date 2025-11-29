---
title: Catalyst Tracker
description: Track catalyst events across multiple sources (PDUFA dates, abstract acceptances, trial completion predictions)
category: tracking
complexity: intermediate
servers:
  - sec_edgar_mcp
  - ct_gov_mcp
patterns:
  - multi_source_aggregation
  - deduplication
  - parameterized_by_time
therapeutic_area: generic
data_type: catalysts
version: 1.0.0
created: 2025-11-29
---

# Catalyst Tracker

Generic catalyst tracking across multiple data sources for any quarter and year.

## Purpose

Aggregates catalyst events from:
1. **PDUFA Tracker** - FDA approval dates from SEC 8-K filings
2. **Abstract Acceptance Tracker** - Conference presentation acceptances from SEC 8-Ks
3. **Trial Completion Predictor** - Predicted conference presentations based on trial completions

## Parameters

- `quarter`: Target quarter (Q1, Q2, Q3, Q4)
- `year`: Target year (e.g., 2025, 2026)
- `companies`: Optional list of company names to track
- `max_companies`: Maximum companies to process (default: 100)
- `include_predicted`: Include trial completion predictions (default: True)
- `min_prediction_probability`: Minimum probability for predictions (default: 0.6)
- `deduplicate`: Remove duplicate catalysts (default: True)

## Usage

```python
from catalyst_tracker.scripts.track_catalysts import track_catalysts

# Track Q1 2026 catalysts
result = track_catalysts(
    quarter="Q1",
    year=2026,
    companies=["Pfizer", "Merck", "Bristol Myers Squibb"],
    include_predicted=True
)

print(f"Total catalysts: {result['total']}")
print(f"By source: {result['by_source']}")
```

## Command Line

```bash
PYTHONPATH=.claude:$PYTHONPATH python3 \
  .claude/skills/catalyst-tracker/scripts/track_catalysts.py
```

## Returns

```python
{
    'quarter': 'Q1 2026',
    'total': 15,
    'catalysts': [
        {
            'source': 'PDUFA',
            'type': 'REGULATORY_APPROVAL',
            'company': 'Pfizer',
            'event': 'PDUFA date: Drug XYZ',
            'date': '2026-03-15',
            'details': {...}
        },
        ...
    ],
    'by_source': {'PDUFA': 5, 'ABSTRACT': 3, 'PREDICTION': 7},
    'by_company': {'Pfizer': 4, 'Merck': 6, ...},
    'summary': {...},
    'errors': []
}
```

## Notes

- SEC 8-K sources (PDUFA, abstracts) typically return 0 results since companies don't file 8-Ks for these events
- Predictions are based on trial completion timing + conference schedule matching
- Deduplication removes catalysts with identical (company, event, date) tuples
- Generic and parameterized - works for any time period
