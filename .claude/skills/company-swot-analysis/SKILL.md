---
name: generate_company_swot_analysis
description: >
  Generate comprehensive strategic SWOT analysis for pharmaceutical and biotechnology
  companies by collecting data from 5 MCP servers: clinical trials (ClinicalTrials.gov),
  financial data (SEC EDGAR), FDA approved products, patent portfolio (USPTO/Google Patents),
  and market performance (Yahoo Finance). Creates evidence-based assessment of Strengths,
  Weaknesses, Opportunities, and Threats with supporting data from regulatory filings,
  clinical development pipelines, intellectual property portfolios, and market metrics.

  Use this skill when you need strategic competitive intelligence on pharmaceutical companies,
  biotech acquisition targets, or investment analysis. Triggers: "company analysis",
  "competitive assessment", "strategic evaluation", "company SWOT", "pharma company profile",
  "biotech company analysis".
category: strategic-analysis
mcp_servers:
  - ct_gov_mcp
  - sec_edgar_mcp
  - fda_mcp
  - uspto_patents_mcp
  - financials_mcp
patterns:
  - multi_server_query
  - markdown_parsing
  - json_parsing
  - data_aggregation
  - strategic_analysis
  - cli_arguments
  - sec_xbrl_parsing
  - status_filtering
  - pagination
data_scope:
  total_results: 5 data sources
  geographical: Global (US-focused for regulatory data)
  temporal: Active clinical pipeline (recruiting/ongoing only) and current financial data
created: 2025-11-27
last_updated: 2025-11-27
complexity: complex
execution_time: ~30-60 seconds
token_efficiency: ~99% reduction vs raw data
cli_enabled: true
version: 1.1
---
# generate_company_swot_analysis


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What generate company swot analysis drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved generate company swot analysis medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for generate company swot analysis`


## Purpose

Generate comprehensive strategic SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis for pharmaceutical and biotechnology companies by integrating data from multiple authoritative sources.

## Usage

**When to use this skill:**
- Strategic evaluation of pharmaceutical/biotech companies
- Competitive intelligence gathering
- Investment due diligence and analysis
- Acquisition target assessment
- Partnership opportunity evaluation
- Market entry strategy development

**Trigger keywords:**
- "company analysis", "competitive assessment", "strategic evaluation"
- "company SWOT", "pharma company profile", "biotech company analysis"
- "competitive intelligence", "strategic position", "market position"

## Data Sources (5 MCP Servers)

### 1. Active Clinical Pipeline (ct_gov_mcp)
- **Source:** ClinicalTrials.gov registry
- **Data Collected:**
  - **Active trials only** (recruiting, not yet recruiting, active not recruiting, enrolling by invitation)
  - Excludes historical completed/terminated/suspended/withdrawn trials
  - Phase distribution (Phase 1/2/3/4) for active trials
  - Current recruitment status distribution
  - Therapeutic areas and indications
- **Analysis Use:** Current R&D investment, pipeline depth, development capabilities, strategic focus areas
- **Pagination:** Full data collection with pageToken support (pageSize=5000)

### 2. Financial Data (sec_edgar_mcp)
- **Source:** SEC EDGAR filings (10-K, 10-Q)
- **Data Collected:**
  - Annual revenue trends
  - R&D spending and ratio to revenue
  - Profitability metrics
  - Operating expenses
- **Analysis Use:** Financial performance, R&D efficiency, commercial viability

### 3. Approved Products (fda_mcp)
- **Source:** FDA drugs database
- **Data Collected:**
  - Total approved products count
  - Product names and brands
  - Therapeutic classification
  - Approval indications
- **Analysis Use:** Commercial portfolio strength, market presence, revenue diversification

### 4. Patent Portfolio (uspto_patents_mcp)
- **Source:** USPTO via Google Patents
- **Data Collected:**
  - Total US patent count
  - Publication year trends
  - Patent families
  - Technology areas
- **Analysis Use:** IP protection, innovation trajectory, exclusivity runway

### 5. Market Performance (financials_mcp)
- **Source:** Yahoo Finance
- **Data Collected:**
  - Market capitalization
  - Current stock price
  - P/E ratio
  - 52-week range
- **Analysis Use:** Market valuation, investor sentiment, financial health

## SWOT Categorization Framework

### Strengths (Identified From)
- ✅ **Product Revenue:** Blockbuster products (>$1B annual sales), strong revenue growth (>20% YoY)
- ✅ **Product Innovation:** Large clinical pipeline (>20 trials), diverse therapeutic areas
- ✅ **Strategic Partnerships:** Multiple collaborations with big pharma
- ✅ **Patent Protection:** Strong patent portfolio (>50 patents), long exclusivity runway
- ✅ **Financial Performance:** Sustained profitability, positive cash flow

### Weaknesses (Identified From)
- ⚠️ **Limited Pipeline:** Few late-stage trials (<5 Phase 3 programs)
- ⚠️ **Clinical Gaps:** Trial terminations, development setbacks
- ⚠️ **Patent Expiry:** Near-term patent cliffs (<5 years to expiry)
- ⚠️ **Revenue Concentration:** Single product dependency
- ⚠️ **Expense Growth:** R&D spending >30% of revenue

### Opportunities (Identified From)
- 🚀 **Market Expansion:** Active recruiting trials, label expansion potential
- 🚀 **Early Pipeline:** Multiple Phase 1/2 programs (>5)
- 🚀 **Strategic Licensing:** Partnership opportunities
- 🚀 **Next-Gen Products:** Follow-on molecules, improved formulations

### Threats (Identified From)
- 🔴 **Generic Competition:** Patent expiry approaching, ANDA filings
- 🔴 **Competitive Landscape:** Rival programs in same therapeutic areas
- 🔴 **Development Risk:** Historical trial failures, terminated programs
- 🔴 **Market Forces:** Pricing pressure, regulatory changes

## Implementation Details

### Multi-Server Data Collection Pattern

The skill follows a proven multi-server pattern:

1. **Parallel data collection** from 5 independent sources
2. **Graceful degradation** - continues if individual server fails
3. **Structured aggregation** - combines heterogeneous data formats
4. **Evidence-based categorization** - each SWOT point backed by data

### Response Formats Handled

- **Markdown parsing:** ClinicalTrials.gov responses (regex extraction)
- **JSON parsing:** FDA, Patents, Financial data (dict traversal)
- **XBRL parsing:** SEC EDGAR financial concepts (simplified extraction)

### Error Handling

Each data source collection includes:
- Try-catch exception handling
- Success/failure flags in return dict
- Detailed error messages for troubleshooting
- Continues execution even if individual sources fail

## Output Structure

```python
{
    'company_name': str,
    'last_updated': str,  # ISO date format
    'data_sources': {
        'clinical_pipeline': {
            'total_trials': int,
            'phase_distribution': dict,
            'status_distribution': dict,
            'therapeutic_areas': dict,
            'success': bool
        },
        'financial_data': {
            'revenue': float,
            'rd_spending': float,
            'success': bool
        },
        'approved_products': {
            'total_products': int,
            'product_names': list,
            'therapeutic_areas': dict,
            'success': bool
        },
        'patent_portfolio': {
            'total_patents': int,
            'publication_years': dict,
            'success': bool
        },
        'market_performance': {
            'market_cap': float,
            'stock_price': float,
            'pe_ratio': float,
            'success': bool
        }
    },
    'swot_analysis': {
        'strengths': [
            {'category': str, 'point': str, 'evidence': str},
            ...
        ],
        'weaknesses': [...],
        'opportunities': [...],
        'threats': [...]
    },
    'formatted_report': str  # Full markdown report
}
```

## Example Usage

### Command Line
```bash
# Default example (Exelixis)
python generate_company_swot_analysis.py

# Custom company
python generate_company_swot_analysis.py "Moderna"

# Another example
python generate_company_swot_analysis.py "Pfizer"
```

### Python Import
```python
from skills.company_swot_analysis.scripts.generate_company_swot_analysis import generate_company_swot_analysis

result = generate_company_swot_analysis("Exelixis")
print(result['formatted_report'])
```

## Report Format

The generated report follows this structure:

1. **Executive Summary** - Strategic position overview (2-3 paragraphs)
2. **Data Sources Summary** - Transparency table showing data provenance
3. **Strengths Section** - Evidence-based competitive advantages
4. **Weaknesses Section** - Strategic vulnerabilities and gaps
5. **Opportunities Section** - Growth and expansion potential
6. **Threats Section** - Competitive and market risks
7. **Sources** - Full data source attribution

## Quality Standards

- ✅ **Evidence-based:** Every SWOT point includes supporting data
- ✅ **Comprehensive:** Integrates 5 independent data sources
- ✅ **Current:** Uses live data from authoritative sources
- ✅ **Transparent:** Clear attribution and data provenance
- ✅ **Actionable:** Strategic insights for decision-making

## Limitations

- **Company name matching:** Requires exact or close match in each database
- **Private companies:** Limited financial data if not publicly traded
- **International data:** Primarily US-focused regulatory/patent data
- **Historical analysis:** Focuses on current state, not deep historical trends
- **Ticker symbols:** Market data requires valid stock ticker

## Related Skills

- `generate_drug_swot_analysis` - SWOT for specific drug products
- `get_company_clinical_trials_portfolio` - Detailed clinical pipeline analysis
- `get_company_segment_geographic_financials` - Deep-dive financial analysis
- `competitive-landscape-analyst` - Strategic agent using this skill

## Verification Checklist

After execution, verify:
- ✅ All 5 data sources attempted (success flags checked)
- ✅ Clinical trials count > 0 (or company not found logged)
- ✅ SWOT has ≥2 points in each category (or data insufficient noted)
- ✅ Report generated in valid markdown format
- ✅ Data sources table populated with actual counts

## Token Efficiency

- **Raw data volume:** ~150,000 tokens (all 5 servers combined)
- **Skill output:** ~2,000 tokens (summary + formatted report)
- **Context reduction:** ~98.7% (following Anthropic code execution pattern)

## Version History

- **v1.1** (2025-11-27): Active pipeline filtering enhancement
  - **Breaking change:** Focus on active/recruiting trials only (not historical data)
  - Filters trials by status: recruiting, not yet recruiting, active not recruiting, enrolling by invitation
  - Excludes completed, terminated, suspended, withdrawn trials
  - Provides true picture of current R&D pipeline for strategic analysis
  - ~95% reduction in trial counts (shows current investment, not 20+ years history)
  - Updated documentation to clarify active pipeline scope

- **v1.0** (2025-11-27): Initial release with 5-server integration
  - Clinical pipeline analysis (ClinicalTrials.gov)
  - Financial data extraction (SEC EDGAR)
  - FDA approved products catalog
  - Patent portfolio analysis (USPTO)
  - Market performance metrics (Yahoo Finance)
  - Evidence-based SWOT categorization
  - CLI argument support
  - Full pagination support (pageSize=5000)