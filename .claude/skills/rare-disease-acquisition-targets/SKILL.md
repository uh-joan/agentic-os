---
name: get_rare_disease_acquisition_targets
description: >
  Identifies potential biotech acquisition targets with rare disease clinical programs in Phase 2 or Phase 3.
  Enhanced with optional DUAL-SOURCE financial intelligence (SEC EDGAR + Yahoo Finance) for comprehensive M&A analysis.

  Uses pattern-based filtering to detect rare disease indicators (orphan designation, ultra-rare, lysosomal storage,
  metabolic disorders) and adaptive phase strategy to capture early-stage companies before late-stage development.

  Yahoo Finance financial enrichment provides (v3.0):
  - Cash runway calculation from operating cash flow (11.5 months for Ultragenyx)
  - 6 distress signals: cash runway, free cash flow, debt-to-equity, quick ratio, negative EPS, low P/E
  - Debt and liquidity analysis: D/E ratio, quick ratio, current ratio
  - Market valuation: Market cap, P/E ratio, EPS, enterprise value
  - Smart ticker lookup: Handles subsidiaries ("Genzyme, a Sanofi Company" → Sanofi) and international companies
  - 28% enrichment coverage (7/25 companies) with comprehensive financials
  - Faster execution (~60% faster than v2.2 - no SEC rate limiting)

  Acquisition scoring ranks targets based on:
  - Clinical validation: Phase (earlier = more acquirable), orphan designation, ultra-rare indication
  - Financial distress: Cash runway, stock performance, and earnings pressure increase acquisition likelihood
  - Portfolio depth: Multiple programs suggest platform potential
  - Market valuation: Market cap determines acquisition feasibility

  Use this skill when:
  - Evaluating M&A opportunities in rare disease biotech
  - Identifying financially distressed companies (cash runway <12-18 months OR stock down >50%)
  - Screening for orphan drug developers with active programs
  - Analyzing competitive landscape in ultra-rare diseases
  - Assessing acquisition targets by financial health and market valuation
  - Comparing US vs international rare disease companies

  Performance: Fast clinical-only mode (~10 sec) or comprehensive dual-source enrichment (~30-60 sec)
category: strategic-analysis
mcp_servers:
  - ct_gov_mcp
  - financials_mcp
patterns:
  - pagination
  - markdown_parsing
  - sponsor_aggregation
  - phase_distribution
  - web_ticker_lookup
  - company_name_preprocessing
  - yahoo_stock_financials_integration
  - cash_runway_calculation
  - distress_signal_detection
  - debt_liquidity_analysis
  - pattern_based_filtering
  - adaptive_phase_strategy
  - acquisition_scoring
data_scope:
  total_results: varies
  geographical: Global
  temporal: Active programs only
  financial_coverage: ~28% (public companies via Yahoo Finance)
  distress_signals: 6 signals (v3.0)
created: 2025-11-26
last_updated: 2025-01-27
version: 3.0
complexity: complex
execution_time: ~10 seconds (clinical only) | ~30-60 seconds (with financials)
token_efficiency: ~99% reduction vs raw trial data
---
# get_rare_disease_acquisition_targets


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for rare disease acquisition targets?`
2. `@agent-pharma-search-specialist Find active rare disease acquisition targets trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for rare disease acquisition targets`


## Purpose

Identifies rare disease companies that are potential acquisition targets using clinical trial data with optional DUAL-SOURCE financial enrichment (SEC EDGAR + Yahoo Finance).

This skill combines two intelligence layers:
1. **Clinical Intelligence**: Pattern-based rare disease detection in ClinicalTrials.gov data
2. **Financial Intelligence (Yahoo Finance)**: Complete financial analysis including:
   - Cash and cash flow (operating, free) → Cash runway calculation
   - Debt and liquidity ratios → Financial health assessment
   - Market valuation (market cap, P/E, EPS) → Acquisition pricing
   - 6 distress signals → M&A timing optimization

## Enhancement Summary (v3.0 - Yahoo Finance Complete Financials)

**MAJOR UPGRADE in v3.0** - SEC EDGAR Eliminated:
- ✅ **Yahoo Finance stock_financials integration** - Complete financial data from single source
- ✅ **Cash runway calculation** - Computed from operating cash flow (no SEC needed!)
- ✅ **6 distress signals** (was 2): Cash runway, free cash flow, debt-to-equity, quick ratio, negative EPS, low P/E
- ✅ **Debt & liquidity analysis** - Debt-to-equity ratio, quick ratio, current ratio
- ✅ **Faster execution** - Eliminated SEC rate limiting delays (~60% faster)
- ✅ **Same 28% coverage** - Yahoo-only architecture with superior intelligence

**Coverage Reality** (v3.0):
- **Public companies (US + international)**: ~25-30% coverage (Yahoo Finance)
- **Private companies**: 0% coverage (no publicly traded stock)
- **Academic/government**: 0% coverage (non-commercial entities)
- **Tested results**: 7/25 companies enriched with comprehensive financials
- **Architecture**: Yahoo Finance only (stock_summary + stock_financials)

**Previous features (v2.2 - v2.0)**:
- ✅ **Web-based ticker lookup** - Yahoo Finance Search API for international companies
- ✅ **Smart company name preprocessing** - Extracts parent companies, removes legal suffixes
- ✅ **Multi-variation search** - Tries multiple name formats for maximum ticker discovery

**Previous features (v2.0)**:
- ✅ SEC EDGAR financial data integration
- ✅ Fuzzy company name matching (handles "Inc.", "Corp.", "Therapeutics" variations)
- ✅ Cash runway calculation: `months_of_cash = cash / (R&D_expense / 12)`
- ✅ Distress signal detection (low cash <12 months, negative earnings)
- ✅ Cash runway filtering (`max_cash_runway_months` parameter)
- ✅ Graceful handling of private companies (clinical scoring only)
- ✅ Optional enrichment (default: False for performance)
- ✅ Enhanced acquisition scoring with financial factors

## Usage

### Basic Usage (Clinical Data Only - Fast)
```python
from .claude.skills.rare_disease_acquisition_targets.scripts.get_rare_disease_acquisition_targets import get_rare_disease_acquisition_targets

# Fast screening without financial data (~10 seconds)
result = get_rare_disease_acquisition_targets(
    therapeutic_focus='ultra_rare_metabolic',
    max_results=30
)
```

### With Financial Enrichment (Comprehensive - Dual Source)
```python
# Include BOTH SEC EDGAR + Yahoo Finance metrics (~30-60 seconds)
# Automatically queries both sources to maximize coverage
result = get_rare_disease_acquisition_targets(
    therapeutic_focus='ultra_rare_metabolic',
    enrich_financials=True,
    max_results=30
)

# Result will show:
# - SEC EDGAR data (if US public company): Cash, R&D, runway
# - Yahoo Finance data (if public): Market cap, stock price, P/E ratio
# - Combined distress signals from both sources
```

### Distress Signal Filtering
```python
# Filter for financially distressed companies only
result = get_rare_disease_acquisition_targets(
    therapeutic_focus='any',
    enrich_financials=True,
    max_cash_runway_months=18,  # Companies with <18 months cash
    max_results=50
)
```

### Standalone Execution
```bash
# Default execution with financial enrichment
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/rare-disease-acquisition-targets/scripts/get_rare_disease_acquisition_targets.py

# Fast clinical-only mode (modify __main__ block)
# Set enrich_financials=False in the script
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `therapeutic_focus` | str | 'any' | Therapeutic area: 'ultra_rare_metabolic', 'neuromuscular', 'gene_therapy', 'oncology_rare', 'any' |
| `min_programs` | int | 1 | Minimum trials per company (filter out single-program companies) |
| `max_programs` | int | 8 | Maximum trials per company (filter out large pharma) |
| `exclude_academic` | bool | True | Exclude universities and medical centers (pattern-based detection) |
| `exclude_government` | bool | True | Exclude NIH, NCI, and other government agencies |
| `exclude_cro` | bool | True | Exclude contract research organizations |
| `prefer_phase3` | bool | True | Adaptive phase strategy: Try Phase 3 first, expand to Phase 2 if <20 companies |
| `max_results` | int | 50 | Maximum number of ranked targets to return |
| `enrich_financials` | bool | False | **Enable SEC EDGAR financial data lookup** (slower but adds cash runway, distress signals) |
| `max_cash_runway_months` | float | None | Filter for distressed companies (requires `enrich_financials=True`) |

## Returns

```python
{
    'query_strategy': {
        'therapeutic_focus': str,
        'phases_included': str,  # 'PHASE3 only' or 'PHASE2+PHASE3'
        'phase_expansion_reason': str,
        'financial_enrichment': bool
    },
    'filtering_summary': {
        'total_trials': int,
        'companies_before_filtering': int,
        'excluded_academic': int,
        'excluded_government': int,
        'excluded_large_pharma': int,
        'excluded_cro': int,
        'excluded_small_portfolio': int,
        'companies_after_filtering': int
    },
    'top_targets': [
        {
            'rank': int,
            'sponsor': str,
            'acquisition_score': int,  # 0-100+
            'total_programs': int,
            'phase2_count': int,
            'phase3_count': int,
            'recruiting_count': int,
            'lead_asset': {
                'nct_id': str,
                'intervention': str,
                'condition': str,
                'phase': str,
                'status': str
            },
            'financial_metrics': {  # Only if enrich_financials=True
                'company_name': str,
                'cik': str,
                'ticker': str,
                'cash_millions': float,
                'rd_expense_millions': float,
                'cash_runway_months': float,
                'distress_signals': List[str]  # e.g., ['Low cash runway (8.3 months)', 'Negative earnings ($45M loss)']
            } | None,
            'all_programs': List[dict]
        }
    ],
    'summary': str  # Markdown-formatted summary
}
```

## Implementation Details

### Pattern-Based Rare Disease Detection

**No hardcoded company names** - uses keywords only:

```python
THERAPEUTIC_QUERIES = {
    'ultra_rare_metabolic': 'lysosomal storage OR mitochondrial disease OR organic acidemia OR urea cycle OR peroxisomal',
    'neuromuscular': 'muscular dystrophy OR spinal muscular atrophy OR myasthenia gravis OR neuropathy',
    'gene_therapy': 'gene therapy OR AAV OR lentiviral OR adenoviral OR CRISPR',
    'oncology_rare': 'rare cancer OR orphan cancer OR sarcoma OR mesothelioma',
    'any': 'orphan OR "rare disease"'
}
```

### Adaptive Phase Strategy

**Intelligent expansion** to ensure sufficient results:

1. **Try Phase 3 first** (most de-risked programs)
2. **Check result count**: If <20 companies found
3. **Expand to Phase 2**: Combine Phase 2 + Phase 3 trials
4. **Report strategy**: Transparent reporting of expansion decision

### Financial Enrichment Process

**Step 1: Fuzzy Company Name Matching**
```python
# Handles variations:
# CT.gov: "Ultragenyx Pharmaceutical Inc."
# SEC: "Ultragenyx Pharmaceutical Inc"
# Match: 95% similarity → Success

# Normalization:
# - Remove suffixes: Inc., Corp., Ltd., LLC, Therapeutics, Pharma, Bio
# - Lowercase and strip whitespace
# - Calculate similarity ratio (threshold: 60%)
```

**Step 2: SEC EDGAR Data Extraction (US Companies)**
- Search company by name (`search_companies`)
- Get CIK (Central Index Key)
- Retrieve company facts (`get_company_facts`)
- Extract metrics from 10-K filings:
  - `CashAndCashEquivalentsAtCarryingValue` → Cash on hand
  - `ResearchAndDevelopmentExpense` (annual) → R&D burn rate
  - `NetIncomeLoss` → Profitability
  - `CommonStockSharesOutstanding` → Shares
- Extract ticker symbol from SEC data (if available)

**Step 2b: Yahoo Finance Ticker Lookup (Global Companies)**
When SEC doesn't provide ticker (international/private companies):
```python
# Smart company name preprocessing:
1. Extract parent: "Genzyme, a Sanofi Company" → "Sanofi"
2. Remove legal suffix: "Novartis Pharmaceuticals" → "Novartis"
3. Try variations: [parent_name, base_name, original_name]

# Yahoo Finance Search API:
GET https://query2.finance.yahoo.com/v1/finance/search?q={company_name}
- Returns: Ticker symbols with company metadata
- Filters: Only EQUITY securities (no funds/ETFs)
- Matching: Fuzzy name matching on long_name/short_name
```

**Step 3: Yahoo Finance Market Data**
- Parse markdown response from `financials_mcp.stock_summary(ticker)`
- Extract: Market cap, stock price, P/E ratio, EPS, beta
- Calculate distress signals (negative EPS, low P/E <5)

**Step 4: Cash Runway Calculation**
```python
monthly_burn = rd_expense_millions / 12
cash_runway_months = cash_millions / monthly_burn

# Example:
# Cash: $50M
# Annual R&D: $48M → Monthly burn: $4M
# Runway: 50 / 4 = 12.5 months
```

**Step 4: Distress Signal Detection**
- **Low cash runway**: < 12 months
- **Negative earnings**: Annual net income < 0

### Acquisition Scoring System

**Base Clinical Scores**:
- Portfolio sweet spot (2-5 programs): +30 points
- Has Phase 3 (de-risked): +25 points
- Multiple programs (platform): +20 points
- Active recruiting (momentum): +15 points
- Balanced Phase 2+3: +10 points

**Financial Modifiers** (if `enrich_financials=True`):
- **Each distress signal**: +5 points
  - Low cash runway (<12 months): +5
  - Negative earnings: +5
  - Both signals: +10 total

**Interpretation**:
- **Score 80+**: Exceptional target (sweet spot portfolio + Phase 3 + recruiting + distressed)
- **Score 60-79**: High priority target (strong clinical + some distress)
- **Score 40-59**: Medium priority target
- **Score <40**: Lower priority target

## Use Cases

### 1. Fast Clinical Screening (No Financial Data)
**Scenario**: Quick landscape scan of rare disease companies
```python
result = get_rare_disease_acquisition_targets()
# Returns: All rare disease sponsors, ranked by clinical score only
# Time: ~10 seconds
```

### 2. Distressed Company Identification
**Scenario**: Find companies likely to need funding/exit soon
```python
result = get_rare_disease_acquisition_targets(
    enrich_financials=True,
    max_cash_runway_months=12  # <12 months cash
)
# Returns: Companies with low cash runway, ranked by acquisition score
# Time: ~30-60 seconds
```

### 3. Therapeutic Area Focus with Financials
**Scenario**: Evaluate acquisition targets in neuromuscular diseases
```python
result = get_rare_disease_acquisition_targets(
    therapeutic_focus='neuromuscular',
    enrich_financials=True,
    max_results=20
)
# Returns: Top 20 neuromuscular rare disease companies with financial metrics
```

### 4. Platform Company Identification
**Scenario**: Find companies with multiple programs (platform potential)
```python
result = get_rare_disease_acquisition_targets(
    min_programs=3,  # At least 3 programs
    enrich_financials=True
)
# Returns: Multi-program rare disease platforms with financial health data
```

## Performance Characteristics

| Configuration | Execution Time | Targets Scanned | Financial Lookups | Use Case |
|---------------|----------------|-----------------|-------------------|----------|
| Clinical only | ~10 seconds | 50-100 sponsors | 0 | Fast screening |
| With financials (all) | ~60 seconds | 50-100 sponsors | 50-100 API calls | Comprehensive analysis |
| With financials (filtered) | ~30-45 seconds | 50-100 sponsors | 20-40 API calls | Distress signal focus |

**Token Efficiency**:
- **Clinical only**: ~99.5% reduction (only summary + top targets)
- **With financials**: ~99.2% reduction (adds financial metrics to summary)
- **Raw data never enters context**: All processing in execution environment

## Data Quality

**Verification Results** (v2.0):
- ✅ Execution: No errors, clean exit
- ✅ Data Retrieved: Successfully queries CT.gov and SEC EDGAR
- ✅ Pagination: Complete dataset retrieved
- ✅ Fuzzy Matching: Handles company name variations
- ✅ Financial Calculation: Cash runway formula verified
- ✅ Distress Detection: Correctly identifies low cash and negative earnings
- ✅ Executable: Standalone execution verified
- ✅ Importable: Can be imported as Python module

**Known Limitations**:
1. **Coverage constraint (~25-30% enrichment)** - IMPROVED in v2.2:
   - ✅ SOLVED: International public companies now enriched via Yahoo Finance Search API
   - ✅ SOLVED: Subsidiary/division names handled via smart preprocessing
   - ✅ Examples: "Genzyme, a Sanofi Company" → Sanofi, "Novartis Pharmaceuticals" → Novartis
   - ❌ REMAINING: Private companies still 0% coverage (no publicly traded stock)
   - ❌ REMAINING: Academic/government entities 0% coverage (non-commercial)
   - Tested results: 7/25 companies (28%) successfully enriched

2. **Private company limitation** - INHERENT:
   - Many rare disease biotechs are private (no ticker symbol exists)
   - Examples: Bioprojet, AOP Orphan, Rapa Therapeutics
   - No public financial data available without private funding database
   - Cannot be solved without access to Crunchbase/PitchBook APIs

3. **Rate limiting overhead**:
   - SEC EDGAR has strict rate limits (10 req/sec)
   - Added 150ms delay + exponential backoff = slower execution (~30-60 sec with financials)
   - Many failed lookups waste time (international companies not in SEC)

4. **Fuzzy matching**: May miss alternative company names (e.g., subsidiaries, parent companies)

5. **Recent funding**: Not detected (would need additional data source like Crunchbase)

## Error Handling

**Graceful Degradation**:
- **Private companies**: Included in results, no financial metrics
- **API failures**: Continue processing, log error, return partial results
- **Missing financial fields**: Calculate what's available, mark others as N/A
- **Fuzzy match failures**: Fallback to first search result

**Example Output**:
```
  Enriching: Ultragenyx Pharmaceutical Inc... ✓ (2 distress signals)
  Enriching: BioMarin Pharmaceutical... ✓ (0 distress signals)
  Enriching: Private Biotech Corp... ✗ (not found)
```

## Future Enhancements

**Completed in v2.2**:
- ✅ **Web-based ticker lookup** - Yahoo Finance Search API implementation
- ✅ **Smart company name preprocessing** - Handles subsidiaries and legal suffixes
- ✅ **International company coverage** - 28% enrichment achieved (up from 0%)

**Planned Features** (v3.0):
1. Crunchbase/PitchBook integration for private company valuations
2. Patent portfolio analysis (USPTO MCP) for IP value assessment
3. Publication analysis (PubMed MCP) for scientific credibility
4. Recent funding detection (SEC Form D filings, press releases)
5. Geographic filtering (US vs EU rare disease companies)
6. Collaboration/partnership history (strategic fit assessment)
7. Real-time stock alerts for distress signals (price drops >30%)

## Related Skills

- `get_orphan_drug_designations` - FDA orphan drug analysis
- `get_company_segment_geographic_financials` - SEC financial data (deep dive)
- `get_clinical_trial_timeline_analysis` - Program timeline assessment
- `get_kras_inhibitor_trials` - Reference for pagination and markdown parsing patterns

## Metadata

- **Category**: Strategic Analysis / M&A Intelligence
- **Servers**: ct_gov_mcp, sec_edgar_mcp, financials_mcp (Yahoo Finance)
- **Complexity**: Complex (triple-server integration, fuzzy matching, rate limiting, dual-source financial enrichment)
- **Token Efficiency**: 99% reduction (clinical-only) | 99.2% reduction (with dual-source financials)
- **Execution Time**: ~10 seconds (clinical-only) | ~30-60 seconds (with dual-source financials + rate limiting)
- **Coverage**: ~10-15% enrichment (US public companies only) - Limited by ticker discovery constraint
- **Version**: 2.1 (Yahoo Finance markdown parsing + SEC ticker extraction + rate limiting)