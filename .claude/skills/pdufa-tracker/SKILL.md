# PDUFA Date Tracker


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What are upcoming catalysts for pdufa-tracker?`
2. `@agent-pharma-search-specialist Show me PDUFA dates for pdufa-tracker drugs`
3. `@agent-pharma-search-specialist Find clinical trial readouts in pdufa-tracker`


## Overview

Tracks FDA Prescription Drug User Fee Act (PDUFA) action dates by monitoring SEC 8-K filings. PDUFA dates are the exact dates when FDA must make approval decisions on new drug applications.

**Key Catalyst**: PDUFA decisions cause 50-200% stock moves (approval vs rejection).

## What are PDUFA Dates?

When FDA accepts a New Drug Application (NDA) or Biologics License Application (BLA), they assign a PDUFA date - the deadline for FDA to make an approval decision.

**Timeline:**
```
Company submits NDA → FDA accepts (60 days) → PDUFA date assigned (6-10 months out) → FDA decision (PDUFA date)
```

**Why Track Them:**
- Known 6-12 months in advance (filed in 8-K)
- Exact dates (not estimates)
- Binary outcomes: approval ✓ or rejection ✗
- Massive stock moves (50-200%)

## How It Works

1. **Search SEC EDGAR 8-K filings** for PDUFA-related keywords
2. **Parse filings** to extract PDUFA dates and drug names
3. **Filter to target quarter** (e.g., Q4 2025 = Oct-Dec 2025)
4. **Return companies** with upcoming PDUFA decisions

## Data Source

**SEC EDGAR 8-K Filings** - Current Report (Material Events)

Companies file 8-Ks within 4 business days of FDA acceptance, announcing:
- Drug name
- Indication
- PDUFA date assigned by FDA
- Review type (standard 10 months vs priority 6 months)

## Expected Results (Q4 2025 Example)

**Input**: Q4 2025 (Oct-Dec 2025)

**Output**: ~10-15 PDUFA dates

Example:
```
| Company | Drug | Indication | PDUFA Date | Filing Date |
|---------|------|------------|------------|-------------|
| Amgen | Tarlatamab | Small Cell Lung Cancer | Dec 12, 2025 | May 14, 2025 |
| BMS | KarXT | Schizophrenia | Nov 22, 2025 | Apr 18, 2025 |
| ... | ... | ... | ... | ... |
```

## Usage

```python
from .claude.skills.pdufa_tracker.scripts.track_pdufa_dates import track_pdufa_dates

# Find all PDUFA dates in Q4 2025
result = track_pdufa_dates(
    quarter="Q4",
    year=2025,
    lookback_months=12  # Search filings from last 12 months
)

# Result:
{
    'quarter': 'Q4 2025',
    'total_pdufa_dates': 12,
    'pdufa_dates': [
        {
            'company': 'Amgen',
            'ticker': 'AMGN',
            'drug': 'Tarlatamab',
            'indication': 'Small Cell Lung Cancer',
            'pdufa_date': '2025-12-12',
            'filing_date': '2025-05-14',
            'review_type': 'Priority Review',
            'cik': '0000318154'
        },
        # ... 11 more
    ]
}
```

## Parameters

- `quarter`: "Q1", "Q2", "Q3", "Q4"
- `year`: 2025, 2026, etc.
- `lookback_months`: How far back to search 8-K filings (default: 12 months)
- `companies`: Optional list of companies to filter (default: all)

## Integration with Discovery

After bottom-up discovery finds ~308 companies:
1. Run PDUFA tracker on all companies
2. Identify companies with PDUFA dates in target quarter
3. Add to catalyst calendar as "CONFIRMED" catalysts (exact dates)

---

**Category**: Catalyst Tracking
**Servers**: sec_edgar_mcp
**Patterns**: 8-K filing search, Date extraction, Regex parsing
**Complexity**: Medium (filing search + text parsing)
**Estimated Runtime**: 2-3 minutes (search + parse 100+ filings)