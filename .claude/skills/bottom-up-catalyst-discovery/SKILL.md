# Bottom-Up Catalyst Discovery


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for bottom-up-catalyst-discovery?`
2. `@agent-pharma-search-specialist Find active bottom-up-catalyst-discovery trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for bottom-up-catalyst-discovery`


## Overview

Automated bottom-up discovery pipeline that starts from ClinicalTrials.gov trials and builds a comprehensive list of investable biotech companies with upcoming catalysts.

**Approach**: Trial-driven discovery (not watchlist-driven)

**Output**: 308 investable public biotechs with quarterly catalysts

## Pipeline Steps

1. **Extract Sponsors** - Get all sponsors from Phase 2/3 trials completing in target quarter
2. **Filter Academic** - Remove universities, hospitals, government institutions (keyword-based)
3. **Lookup Tickers** - Use WebSearch to find stock ticker symbols (automated)
4. **Validate Public** - Confirm public company status via SEC EDGAR
5. **Enrich Market Cap** - Get market capitalization from Yahoo Finance
6. **Filter by Size** - Keep companies with market cap > $500M

## Key Innovation

**WebSearch Ticker Lookup**: Fully automated ticker discovery eliminates manual lookup table maintenance.

```python
query = f"{company_name} stock ticker symbol"
result = web_search(query=query)
# "AbbVie stock ticker symbol" → "ABBV (NYSE)"
```

## Data Sources

- **ClinicalTrials.gov**: Trial completion dates, sponsors, phases
- **WebSearch**: Automated ticker symbol lookup
- **SEC EDGAR**: Public company validation (CIK mapping)
- **Yahoo Finance**: Market capitalization, stock data

## Expected Results (Q4 2025 Example)

| Step | Input | Output | Automation |
|------|-------|--------|------------|
| 1. Extract sponsors | 5,000 trials | 2,500 sponsors | ✅ 100% |
| 2. Filter academic | 2,500 sponsors | 800 companies | ✅ 90% |
| 3. Lookup tickers | 800 companies | 300 with tickers | ✅ 100% |
| 4. Validate public (SEC) | 300 companies | 280 public | ✅ 100% |
| 5. Enrich market cap | 280 companies | 250 with data | ✅ 95% |
| 6. Filter > $500M | 250 companies | 180 investable | ✅ 100% |

**Total Time**: 3-4 hours execution (fully automated)

## Usage

```python
from .claude.skills.bottom_up_catalyst_discovery.scripts.discover_catalyst_candidates import discover_catalyst_candidates

# Discover companies with Q4 2025 catalysts
candidates = discover_catalyst_candidates(
    quarter="Q4",
    year=2025,
    phases=["PHASE2", "PHASE3"],
    min_market_cap=500_000_000
)

# Result:
{
    'quarter': 'Q4 2025',
    'total_companies': 180,
    'companies': [
        {
            'company_name': 'Arcellx, Inc.',
            'ticker': 'ACLX',
            'market_cap': 2_450_000_000,
            'exchange': 'NASDAQ',
            'trial_count': 3,
            'indications': ['Multiple Myeloma'],
            'catalyst_confidence': 'HIGH'
        },
        # ... 179 more
    ]
}
```

## Parameters

- `quarter`: "Q1", "Q2", "Q3", "Q4"
- `year`: 2025, 2026, etc.
- `phases`: List of trial phases (default: ["PHASE2", "PHASE3"])
- `min_market_cap`: Minimum market cap filter (default: $500M)
- `countries`: Optional country filter (default: all)
- `therapeutic_areas`: Optional therapeutic area filter (default: all)

## Advantages Over Top-Down

✅ **Completeness**: Discovers ALL companies with trials (not just pre-curated list)
✅ **Fresh Discovery**: Finds newly public companies automatically
✅ **No Maintenance**: No manual watchlist to maintain
✅ **Fully Automated**: WebSearch ticker lookup eliminates manual work
✅ **Unbiased**: Doesn't miss small/unknown companies

## Integration with Trackers

Bottom-up discovery creates the initial candidate list. Then run trackers on candidates:

1. **Bottom-Up Discovery** (once before quarter) → 180 companies
2. **PDUFA Tracker** (scan 8-K filings for each company)
3. **Abstract Tracker** (monitor abstract acceptances for each company)
4. **Trial Predictor** (predict conference presentations based on completion dates)

---

**Category**: Catalyst Discovery
**Servers**: ct_gov_mcp, sec_edgar_mcp, financials_mcp, web_search
**Patterns**: Pagination, Multi-server aggregation, Web enrichment, Market cap filtering
**Complexity**: High (multi-step pipeline, cross-referencing)
**Estimated Runtime**: 3-4 hours (1,000+ API calls)