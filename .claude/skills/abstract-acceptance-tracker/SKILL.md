# Abstract Acceptance Tracker


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist Get abstract-acceptance-tracker data`
2. `@agent-pharma-search-specialist Show me abstract-acceptance-tracker information`
3. `@agent-pharma-search-specialist Find abstract-acceptance-tracker details`


## Overview

Tracks conference abstract acceptance announcements by monitoring SEC 8-K filings. Abstract acceptances are early signals of upcoming clinical data presentations 4-8 weeks before conferences.

**Key Catalyst**: Abstract acceptances often cause 10-30% stock moves (oral > poster).

## What are Abstract Acceptances?

When a company's clinical trial abstract is accepted for presentation at a major medical conference, they typically announce it via SEC 8-K filing within 4 business days.

**Timeline:**
```
Abstract submission → Conference review (2-3 months) → Acceptance notification → 8-K filing (4 days) → Conference presentation (4-8 weeks)
```

**Why Track Them:**
- Known 4-8 weeks before conference (filed in 8-K)
- Signals upcoming data readout
- Oral presentations more impactful than posters
- Conference timing known in advance (predictable catalysts)

## Major Conferences Tracked

| Conference | Focus | Timing | Impact |
|------------|-------|--------|--------|
| ASH | Blood cancers (MM, leukemia, lymphoma) | December | HIGH |
| ASCO | All cancers | June | HIGH |
| ESMO | All cancers (EU focus) | September | HIGH |
| ADA | Diabetes, obesity | June | HIGH |
| CTAD | Alzheimer's disease | October/November | MEDIUM |
| ACC | Cardiovascular | March | MEDIUM |
| AACR | Cancer research (early stage) | April | MEDIUM |

## How It Works

1. **Search SEC EDGAR 8-K filings** for abstract acceptance keywords
2. **Parse conference details** (name, dates, presentation type)
3. **Extract clinical details** (drug, indication, trial phase)
4. **Filter to target quarter** (e.g., Q4 2025 = Oct-Dec 2025)
5. **Return companies** with upcoming conference presentations

## Data Source

**SEC EDGAR 8-K Filings** - Current Report (Material Events)

Companies file 8-Ks within 4 business days of abstract acceptance, announcing:
- Conference name (ASH, ASCO, etc.)
- Presentation type (oral vs poster)
- Drug name and indication
- Trial identifier (NCT number)
- Expected presentation date

## Expected Results (Q4 2025 Example)

**Input**: Q4 2025 (Oct-Dec 2025)

**Output**: ~15-25 abstract acceptances

Example:
```
| Company | Drug | Indication | Conference | Date | Type |
|---------|------|------------|------------|------|------|
| Arcellx | CART-ddBCMA | Multiple Myeloma | ASH 2025 | Dec 7-10 | Oral |
| Lilly | Donanemab | Alzheimer's | CTAD 2025 | Oct 29-Nov 1 | Oral |
| ... | ... | ... | ... | ... | ... |
```

## Usage

```python
from .claude.skills.abstract_acceptance_tracker.scripts.track_abstract_acceptances import track_abstract_acceptances

# Find all abstract acceptances in Q4 2025
result = track_abstract_acceptances(
    quarter="Q4",
    year=2025,
    lookback_months=6  # Search filings from last 6 months
)

# Result:
{
    'quarter': 'Q4 2025',
    'total_acceptances': 18,
    'acceptances': [
        {
            'company': 'Arcellx, Inc.',
            'ticker': 'ACLX',
            'drug': 'CART-ddBCMA',
            'indication': 'Multiple Myeloma',
            'conference': 'ASH 2025',
            'conference_dates': '2025-12-07 to 2025-12-10',
            'presentation_type': 'Oral',
            'filing_date': '2025-10-15',
            'trial_id': 'NCT12345678',
            'cik': '0001786205'
        },
        # ... 17 more
    ]
}
```

## Parameters

- `quarter`: "Q1", "Q2", "Q3", "Q4"
- `year`: 2025, 2026, etc.
- `lookback_months`: How far back to search 8-K filings (default: 6 months)
- `conferences`: Optional list of conferences to filter (default: all)
- `presentation_type`: Optional filter ("oral", "poster", or both)

## Integration with Discovery

After bottom-up discovery finds ~308 companies:
1. Run Abstract Acceptance Tracker on all companies
2. Identify companies with presentations in target quarter
3. Add to catalyst calendar as "CONFIRMED" catalysts (known dates)
4. Prioritize oral presentations (higher impact than posters)

## Presentation Type Impact

**Oral Presentation:**
- Selected for most compelling data (top ~10% of abstracts)
- 20-30 minute spotlight with Q&A
- Typical stock move: 20-40% on positive data
- **Higher catalyst value**

**Poster Presentation:**
- Standard acceptance (majority of abstracts)
- Display format, less visibility
- Typical stock move: 5-15% on positive data
- **Lower catalyst value but still trackable**

---

**Category**: Catalyst Tracking
**Servers**: sec_edgar_mcp
**Patterns**: 8-K filing search, Conference parsing, Text extraction
**Complexity**: Medium (filing search + conference matching)
**Estimated Runtime**: 2-3 minutes (search + parse 100+ filings)