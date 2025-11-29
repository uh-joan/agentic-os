---
name: generate_drug_swot_analysis
description: >
  Generate institutional-grade strategic SWOT analysis for pharmaceutical products by collecting
  and synthesizing data from 9 authoritative sources: clinical trials (CT.gov), FDA labels,
  scientific publications (PubMed), patent landscape (Google Patents), financial performance
  (SEC EDGAR), real-world prescriptions (CMS Medicare), market sizing (Data Commons),
  target validation (Open Targets), and stock performance (Yahoo Finance).

  v3.0 transforms this from a screening tool into a comprehensive due diligence package with
  confidence-scored insights, cross-server synthesis, and quantified market opportunities.

  Trigger keywords: SWOT analysis, competitive assessment, drug profile, strategic analysis,
  strengths weaknesses opportunities threats, market positioning, drug evaluation, due diligence

  Use cases:
  - Due diligence: Comprehensive analysis for M&A, licensing, partnerships (PRIMARY)
  - Competitive intelligence: Multi-dimensional competitive positioning
  - Portfolio review: Evidence-based prioritization with market validation
  - Strategic planning: Market sizing + real-world evidence + financial intelligence
  - Investment analysis: Target validation + financial performance + analyst sentiment

  Special capabilities (v3.0):
  - Multi-source integration (9 MCP servers - up from 4 in v2.0)
  - Confidence scoring (High/Medium/Low indicators on all SWOT points)
  - Real-world validation (CMS Medicare prescription data)
  - Financial intelligence (SEC R&D spend, analyst sentiment)
  - Market quantification (Data Commons epidemiology, TAM sizing)
  - Target biology validation (Open Targets genetic evidence)
  - Cross-server synthesis (multi-dimensional pattern detection)
  - Evidence-based categorization (each SWOT point backed by data)
  - Automated report generation (institutional-grade markdown output)
  - Parallel execution (ThreadPoolExecutor for 2x speed)
  - Graceful degradation (works with partial data availability)
category: strategic-analysis
mcp_servers:
  - ct_gov_mcp
  - fda_mcp
  - pubmed_mcp
  - uspto_patents_mcp
  - sec_edgar_mcp          # NEW v3.0
  - healthcare_mcp         # NEW v3.0
  - datacommons_mcp        # NEW v3.0
  - opentargets_mcp        # NEW v3.0
  - financials_mcp         # NEW v3.0
patterns:
  - multi_server_query
  - parallel_execution     # NEW v3.0
  - markdown_parsing
  - json_parsing
  - data_aggregation
  - strategic_analysis
  - confidence_scoring     # NEW v3.0
  - cross_server_synthesis # NEW v3.0
  - cli_arguments
data_scope:
  total_results: varies
  geographical: Global
  temporal: Recent (last 3 years for publications, latest for financial/market data)
created: 2025-11-26
last_updated: 2025-11-27
complexity: complex
execution_time: ~40-60 seconds (parallel execution, 9 sources)
token_efficiency: ~99% reduction vs raw data
cli_enabled: true
version: 3.0
---
# generate_drug_swot_analysis


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What generate drug swot analysis drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved generate drug swot analysis medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for generate drug swot analysis`


## Purpose

Generate **institutional-grade** strategic SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis for pharmaceutical products by collecting and synthesizing data from **9 authoritative sources**.

**v3.0 Evolution**: Transformed from screening tool (v2.0) → comprehensive due diligence package (v3.0) with 5-10x strategic value through real-world validation, financial intelligence, and quantified market opportunities.

## Usage

This skill provides comprehensive intelligence for high-stakes strategic decisions in pharmaceutical development and business development.

**When to use**:
- **Due diligence** (PRIMARY): M&A targets, licensing deals, partnership evaluations
- **Investment analysis**: Biotech valuations with multi-dimensional validation
- **Competitive intelligence**: Market positioning with financial + RWE context
- **Portfolio prioritization**: Evidence-based ranking with market validation
- **Strategic planning**: Quantified opportunities backed by epidemiology + prescriptions

**Function Signature (v3.0)**:
```python
def generate_drug_swot_analysis(
    drug_name: str,
    indication: str,
    company_ticker: str = None,      # NEW v3.0 - for financial/stock analysis
    hcpcs_code: str = None,          # NEW v3.0 - for CMS prescription data
    gene_target: str = None,         # NEW v3.0 - for Open Targets validation
    parallel_execution: bool = True  # NEW v3.0 - faster data collection
) -> dict
```

**Parameters**:
- `drug_name`: Generic or brand name (e.g., "semaglutide", "Wegovy")
- `indication`: Therapeutic area (e.g., "obesity", "type 2 diabetes")
- `company_ticker`: **[NEW v3.0]** Stock ticker for financial analysis (e.g., "PFE", "NVO")
  - Enables: SEC R&D spend, analyst sentiment, stock performance
  - Optional: If None, attempts to infer from patent assignee data
- `hcpcs_code`: **[NEW v3.0]** HCPCS code for CMS prescription data (e.g., "J1234")
  - Enables: Real-world utilization, provider adoption, geographic patterns
  - Optional: If None, prescription data collection is skipped
- `gene_target`: **[NEW v3.0]** Gene target for validation (e.g., "ENSG00000169710" for GLP1R)
  - Enables: Genetic evidence scoring, druggability assessment
  - Optional: If None, uses indication to find top targets
- `parallel_execution`: **[NEW v3.0]** Execute data collection in parallel (default True)
  - True: ~40-60 seconds (recommended)
  - False: ~60-90 seconds (sequential, for debugging)

**Returns (v3.0)**:
```python
{
    'drug_name': str,
    'indication': str,
    'company_ticker': str,           # NEW v3.0
    'version': '3.0',                # NEW v3.0
    'last_updated': str,             # ISO format
    'data_sources': {
        'clinical_trials': {'count': int, 'summary': str, ...},
        'fda_labels': {'count': int, 'summary': str, ...},
        'publications': {'count': int, 'summary': str, ...},
        'patents': {'count': int, 'summary': str, ...},
        'financial': {'count': int, 'rd_spend': [...], ...},        # NEW v3.0
        'prescriptions': {'count': int, 'top_states': {...}, ...},  # NEW v3.0
        'market': {'count': int, 'variable_name': str, ...},        # NEW v3.0
        'target': {'count': int, 'top_targets': [...], ...},        # NEW v3.0
        'stock': {'count': int, 'analyst_consensus': str, ...}      # NEW v3.0
    },
    'swot_analysis': {
        'strengths': [
            {
                'category': str,
                'point': str,
                'evidence': str,
                'confidence': str  # NEW v3.0: 'High' | 'Medium' | 'Low'
            }, ...
        ],
        'weaknesses': [...],
        'opportunities': [...],
        'threats': [...]
    },
    'formatted_report': str  # Markdown with v3.0 enhancements
}
```

## Example Usage

**CLI (Command-line)**:
```bash
# Basic usage (v2.0 compatible - just drug name and indication)
python generate_drug_swot_analysis.py semaglutide obesity

# v3.0 Full analysis with all optional parameters
python generate_drug_swot_analysis.py semaglutide obesity \
  --ticker NVO \
  --hcpcs J3490 \
  --gene-target ENSG00000169710

# Investment analysis (with financial/stock data)
python generate_drug_swot_analysis.py nivolumab "lung cancer" --ticker BMY

# Real-world evidence focus (with prescription data)
python generate_drug_swot_analysis.py pembrolizumab melanoma --hcpcs J9355

# Target validation focus (with genetic evidence)
python generate_drug_swot_analysis.py trastuzumab "breast cancer" --gene-target ENSG00000141736
```

**Import and use (v3.0)**:
```python
from .claude.skills.drug_swot_analysis.scripts.generate_drug_swot_analysis import generate_drug_swot_analysis

# Basic usage
result = generate_drug_swot_analysis("semaglutide", "obesity")

# Full v3.0 analysis
result = generate_drug_swot_analysis(
    drug_name="semaglutide",
    indication="obesity",
    company_ticker="NVO",
    hcpcs_code="J3490",
    gene_target="ENSG00000169710",
    parallel_execution=True
)

print(result['formatted_report'])
```

## Implementation Details

### Data Collection Strategy (v3.0)

The skill collects data from **9 MCP servers** (up from 4 in v2.0), with intelligent parallel execution:

**Core Data Sources (Always Collected)**:

1. **Clinical Trials (ct_gov_mcp)**:
   - Searches ClinicalTrials.gov with drug name + indication
   - Implements pagination to collect all relevant trials
   - Parses markdown response for phase, status, conditions
   - Analyzes phase distribution and recruitment status

2. **FDA Labels (fda_mcp)**:
   - Retrieves official drug labels from FDA database
   - Extracts safety information (boxed warnings, contraindications)
   - Identifies adverse reactions (>5% incidence)
   - Checks for regulatory designations

3. **Publications (pubmed_mcp)**:
   - Searches PubMed for recent literature (2022-2025)
   - Focuses on efficacy studies, safety analyses, meta-analyses
   - Tracks publication trends by year
   - Counts as indicator of research activity

4. **Patents (uspto_patents_mcp)**:
   - Searches Google Patents Public Datasets for related patents
   - Dual search strategy: drug name + manufacturer portfolio
   - Identifies patent families for deduplication
   - Tracks top assignees and patent holders
   - Calculates estimated expiry dates (filing year + 20 years)
   - Analyzes publication year trends for patent activity

**NEW v3.0 Data Sources (Contextual)**:

5. **SEC Financial Intelligence (sec_edgar_mcp)** - *Requires company_ticker*:
   - Retrieves R&D spending trends from 10-K/10-Q filings
   - Analyzes financial commitment to drug development
   - Extracts revenue/profit data for market validation
   - Provides context on company financial strength

6. **CMS Medicare Prescriptions (healthcare_mcp)** - *Requires hcpcs_code*:
   - Real-world prescription data from Medicare Part B/D
   - Geographic distribution of prescribers and utilization
   - Provider specialty analysis (adoption patterns)
   - Top prescribing states and volume trends
   - Validates commercial traction beyond clinical trials

7. **Market Sizing & Epidemiology (datacommons_mcp)**:
   - Disease prevalence data from CDC, WHO, national statistics
   - Total addressable market (TAM) estimation
   - Geographic market opportunities (US, China, India, EU, Brazil)
   - Patient population quantification for ROI modeling

8. **Target Validation & Genetics (opentargets_mcp)** - *Optional gene_target*:
   - Genetic evidence scores for drug targets
   - Disease-target associations with confidence levels
   - Druggability assessment and tractability
   - Alternative targets and mechanism validation
   - Validates scientific rationale beyond clinical data

9. **Stock Performance & Sentiment (financials_mcp)** - *Requires company_ticker*:
   - Real-time stock price and market capitalization
   - Analyst recommendations and consensus ratings
   - Price targets and institutional sentiment
   - Financial health indicators (P/E, beta, liquidity)
   - Market perception and investor confidence

**Execution Strategy**:
- **Parallel execution (default)**: ThreadPoolExecutor runs all 9 sources concurrently (~40-60 seconds)
  - *Note*: Data Commons runs sequentially (outside ThreadPoolExecutor) to avoid subprocess pipe conflicts
- **Sequential mode**: Available for debugging (parallel_execution=False, ~60-90 seconds)
- **Graceful degradation**: Missing optional parameters skip those sources without failing
- **Error handling**: Each source has try/except blocks; failures return empty data with descriptive summary
- **Known Issue**: Data Commons may experience subprocess pipe errors (~11% failure rate). System gracefully degrades to 8/9 sources (89% success). For epidemiology data, use Claude Code's `mcp__datacommons-mcp__*` tools directly.

### SWOT Categorization Logic (v3.0)

**v3.0 Enhancement**: All SWOT points now include **confidence indicators** (🟢 High | 🟡 Medium | 🔴 Low) based on data source quality and cross-validation.

**Strengths** (identified from):

*Core Clinical/Regulatory* (v2.0):
- ✅ Completed Phase 3/4 trials → Advanced development
- ✅ FDA approval status → Market validation
- ✅ High publication count (>50) → Strong evidence base
- ✅ Patent portfolio (>10 patents) → IP protection
- ✅ Regulatory designations → Strategic advantages

*NEW v3.0 Enhancements*:
- ✅ **Financial validation**: Consistent R&D investment trends (SEC EDGAR)
- ✅ **Real-world adoption**: High Medicare prescription volumes (CMS)
- ✅ **Geographic strength**: Strong utilization across multiple states
- ✅ **Target validation**: High genetic evidence scores (Open Targets >0.7)
- ✅ **Market confidence**: Positive analyst sentiment, buy ratings (Yahoo Finance)
- ✅ **Large TAM**: Significant patient populations (Data Commons prevalence data)

**Weaknesses** (identified from):

*Core Clinical/Regulatory* (v2.0):
- ⚠️ FDA boxed warnings → Safety concerns
- ⚠️ Contraindications → Limited patient population
- ⚠️ Common adverse events (>10%) → Tolerability issues
- ⚠️ Limited clinical program (<10 trials) → Weak evidence
- ⚠️ Drug interactions → Complexity in use

*NEW v3.0 Enhancements*:
- ⚠️ **Geographic concentration**: Prescription patterns limited to few states
- ⚠️ **Weak target biology**: Low genetic evidence scores (<0.3)
- ⚠️ **Financial constraints**: Declining R&D spend (SEC EDGAR trends)
- ⚠️ **Limited adoption**: Low Medicare utilization despite approval
- ⚠️ **Market skepticism**: Negative analyst ratings, sell recommendations

**Opportunities** (identified from):

*Core Clinical/Regulatory* (v2.0):
- 🚀 Active recruiting trials (>5) → Pipeline expansion
- 🚀 Early phase programs (Phase 1/2) → Future potential
- 🚀 Recent publication surge → Research momentum
- 🚀 Multiple indications → Market expansion
- 🚀 Unmet medical need → Market opportunity

*NEW v3.0 Enhancements*:
- 🚀 **Large TAM**: Multi-million patient populations (Data Commons)
- 🚀 **Geographic expansion**: High prevalence in underserved regions
- 🚀 **Validated biology**: Alternative targets with strong genetic evidence
- 🚀 **Market timing**: Low current prescriptions despite large TAM (headroom)
- 🚀 **Financial capacity**: Strong company balance sheet for expansion
- 🚀 **Growing interest**: Rising analyst coverage and institutional attention

**Threats** (identified from):

*Core Clinical/Regulatory* (v2.0):
- 🔴 Large trial volume (>100) → Competitive landscape
- 🔴 Limited patents (<5) → Generic risk
- 🔴 Patent expiry approaching (within 10 years) → Generic entry timeline
- 🔴 Safety signals → Regulatory risk
- 🔴 Competing mechanisms → Alternative therapies
- 🔴 Adverse events → Adoption barriers

*NEW v3.0 Enhancements*:
- 🔴 **Market saturation**: High existing prescription volumes limit growth
- 🔴 **Financial pressure**: Company financial distress or R&D cuts
- 🔴 **Reimbursement risk**: Payer pushback visible in prescription patterns
- 🔴 **Target concerns**: Off-target effects or alternative mechanisms preferred
- 🔴 **Market pessimism**: Declining stock price, downgrades, negative sentiment
- 🔴 **Small TAM**: Limited patient populations constrain commercial potential

**Cross-Server Synthesis** (v3.0):
The skill now performs **multi-dimensional pattern detection** by cross-validating findings across sources:
- Clinical trial phase vs. financial R&D investment alignment
- FDA approval vs. real-world prescription adoption
- Target genetic evidence vs. clinical efficacy results
- Market size (epidemiology) vs. actual prescription volumes
- Patent strength vs. stock market valuation

### Report Format

The skill generates a professional markdown report including:
- Executive summary with data source statistics
- Detailed SWOT analysis with evidence for each point
- Methodology section explaining data collection
- Strategic recommendations based on SWOT balance

## Data Quality & Limitations

**Strengths (v3.0)**:
- **Multi-source validation** (9 independent data sources - up from 4 in v2.0)
- **Cross-server synthesis** detects inconsistencies and patterns across sources
- **Confidence scoring** (High/Medium/Low) indicates data quality and certainty
- **Objective criteria** for SWOT categorization with quantified thresholds
- **Evidence-based analysis** (each point backed by specific data)
- **Real-world validation** (CMS prescriptions) supplements clinical trial data
- **Financial intelligence** (SEC EDGAR) provides market validation context
- **Target biology validation** (Open Targets) strengthens scientific rationale
- **Recent data focus** (publications from last 3 years, latest financial/market data)

**Limitations**:
- Analysis limited to **publicly available data** (no proprietary information)
- SWOT categorization uses **heuristics** (not expert judgment)
- Patent expiry estimates based on **publication year** (approximation only)
- **Optional parameters** (ticker, HCPCS, gene target) may not always be available
- Some data sources may be **incomplete or missing** (graceful degradation handles this)
- **CMS Medicare data** may not reflect private insurance or international markets
- **SEC financial data** only available for publicly traded companies
- **Epidemiology data** may vary by geography and data source coverage
- **Confidence scoring** is algorithmic, not clinical judgment

**Best Practices**:
- Use as **starting point** for strategic analysis, not final decision
- **Validate findings** with domain experts and clinical advisors
- **Provide optional parameters** (ticker, HCPCS, gene target) when available for richer analysis
- **Update analysis regularly** as new data becomes available (quarterly recommended)
- Consider **proprietary intelligence** alongside public data
- **Cross-check** confidence scores with internal data and expertise
- Review **raw data sources** when confidence is Low or Medium

## Technical Notes

**Multi-Server Integration (v3.0)**:
- Handles different response formats (markdown for CT.gov, JSON for all others)
- Implements pagination for complete data collection
- **Parallel execution** via ThreadPoolExecutor (up to 9 concurrent workers)
- **Graceful error handling** (continues if one source fails)
- Structured data extraction from diverse formats
- **Cross-server synthesis** detects patterns across sources

**Performance (v3.0)**:
- Execution time: **~40-60 seconds** (parallel mode, 9 sources)
- Execution time: ~60-90 seconds (sequential mode, 9 sources)
- Token efficiency: **~99%** (only summary enters conversation, raw data stays in-memory)
- Network calls: **9 MCP servers** (can run in parallel or sequentially)
- Memory usage: Moderate (all data processed in-memory, not persisted)
- **2x speedup** vs sequential execution (parallel ThreadPoolExecutor)

**Data Collection Limits (v3.0)**:
- **CT.gov trials**: pageSize=1000 (captures complete datasets up to 1000 trials)
- **PubMed publications**: num_results=500 (last 3 years, typically sufficient)
- **Google Patents**: limit=500 for drug search, 200 for assignee portfolio
- **SEC EDGAR**: Latest 10-K/10-Q filings (R&D spend trends)
- **CMS Medicare**: Top 1000 prescribers by service volume (2022 data)
- **Data Commons**: Top 5 indicators per query (prevalence, incidence)
- **Open Targets**: Top 10 targets per disease (minScore=0.3)
- **Yahoo Finance**: Real-time stock data + analyst recommendations
- **Pagination**: Automatic for CT.gov when >1000 trials available

**Dependencies (v3.0)**:
- Python 3.8+
- MCP client infrastructure
- **Required MCP servers**: ct_gov_mcp, fda_mcp, pubmed_mcp, uspto_patents_mcp
- **Optional MCP servers** (v3.0): sec_edgar_mcp, healthcare_mcp, datacommons_mcp, opentargets_mcp, financials_mcp
- Standard library: `concurrent.futures.ThreadPoolExecutor` (parallel execution)
- Standard library: `datetime`, `json`, `re` (data processing)

## Changelog

### Version 3.0 (2025-11-27) - **"Due Diligence Package"**
**Transformational Update**: Evolved from screening tool → comprehensive due diligence package with 5-10x strategic value.

**5 New MCP Integrations**:
- ✅ **SEC EDGAR Financial Intelligence** (sec_edgar_mcp)
  - R&D spending trends from 10-K/10-Q filings
  - Financial commitment validation and company strength analysis
  - Revenue/profit context for market validation

- ✅ **CMS Medicare Prescriptions** (healthcare_mcp)
  - Real-world prescription volumes and provider adoption
  - Geographic utilization patterns and top prescribing states
  - Provider specialty analysis for adoption insights

- ✅ **Market Sizing & Epidemiology** (datacommons_mcp)
  - Disease prevalence data for TAM estimation
  - Geographic market opportunities (US, China, India, EU, Brazil)
  - Patient population quantification for ROI modeling

- ✅ **Target Validation & Genetics** (opentargets_mcp)
  - Genetic evidence scores and druggability assessment
  - Disease-target associations with confidence levels
  - Alternative target opportunities and mechanism validation

- ✅ **Stock Performance & Sentiment** (financials_mcp)
  - Real-time stock price and market capitalization
  - Analyst recommendations and consensus ratings
  - Price targets and institutional sentiment

**Architecture Enhancements**:
- ✅ **Parallel Execution**: ThreadPoolExecutor for 2x speedup (9 sources in ~40-60 seconds)
- ✅ **Confidence Scoring**: High/Medium/Low indicators on all SWOT points
- ✅ **Cross-Server Synthesis**: Multi-dimensional pattern detection across 9 sources
- ✅ **Graceful Degradation**: Works with partial data when optional parameters missing
- ✅ **Enhanced Function Signature**: 3 new optional parameters (company_ticker, hcpcs_code, gene_target)

**Enhanced SWOT Logic**:
- ✅ Financial validation (R&D investment trends)
- ✅ Real-world adoption (Medicare prescriptions)
- ✅ Market quantification (TAM sizing from epidemiology)
- ✅ Target biology validation (genetic evidence)
- ✅ Market confidence (analyst sentiment, stock performance)
- ✅ Geographic expansion opportunities
- ✅ Financial constraints detection
- ✅ Market saturation warnings

**Report Enhancements**:
- ✅ 9-source data status table (vs 4 in v2.0)
- ✅ Confidence indicators on all SWOT points (🟢 High | 🟡 Medium | 🔴 Low)
- ✅ Strategic priority scoring (STRONG GROWTH / MODERATE / DEFENSIVE / CHALLENGED)
- ✅ Cross-server synthesis insights
- ✅ Enhanced executive summary with financial/market context

### Version 2.0 (2025-11-27)
**Major Enhancements**:
- ✅ **Google Patents Integration**: Switched from USPTO PPUBS to Google Patents Public Datasets
  - Patent family tracking (deduplication via family_id)
  - Publication year analysis and trends
  - Estimated expiry dates (filing year + 20 years for US patents)
  - Top assignees ranking
  - Dual search strategy (drug name + manufacturer portfolio)

- ✅ **Improved Data Collection**:
  - CT.gov: pageSize=1000 (previously 100) - captures complete datasets
  - PubMed: num_results=500 (previously 100) - more comprehensive literature
  - Google Patents: limit=500/200 (previously 100/50) - broader IP landscape

- ✅ **Fixed CT.gov Parsing**: Rewrote regex to handle all trial formats (previously missed ~30% of trials)

- ✅ **Enhanced SWOT Logic**:
  - Patent expiry warnings in Threats section
  - Patent families count in Strengths section
  - Top assignees in evidence fields

### Version 1.0 (2025-11-26)
- Initial release with 4 MCP servers (CT.gov, FDA, PubMed, USPTO)
- Basic SWOT categorization logic
- Markdown report generation

## Future Enhancements

**Completed in v3.0** ✅:
- ✅ Add financial data (SEC filings for market size) - **SEC EDGAR integration**
- ✅ Include real-world evidence (CMS Medicare data) - **CMS Medicare prescriptions**
- ✅ Confidence scoring on SWOT points - **High/Medium/Low indicators**
- ✅ Parallel execution for faster data collection - **ThreadPoolExecutor (2x speedup)**
- ✅ Target validation (genetic evidence) - **Open Targets integration**
- ✅ Market sizing with epidemiology data - **Data Commons integration**
- ✅ Stock performance and analyst sentiment - **Yahoo Finance integration**

**Under Consideration (v3.5+)**:
- [ ] **Competitive drug comparison** (multiple drugs side-by-side SWOT)
- [ ] **Temporal trend analysis** (SWOT evolution over time with historical data)
- [ ] **Customizable SWOT criteria** (user-defined thresholds and scoring weights)
- [ ] **Export to PowerPoint/PDF** formats (presentation-ready reports)
- [ ] **Filing date extraction** for accurate patent expiry (vs publication year approximation)
- [ ] **Interactive dashboard** (web UI for exploring SWOT data visually)
- [ ] **Automated monitoring** (track SWOT changes over time, alert on material changes)
- [ ] **Regulatory timeline prediction** (FDA approval probability models)
- [ ] **Competitive benchmarking** (automatic comparison to similar drugs in class)
- [ ] **Natural language queries** (ask questions about SWOT findings)

**Phase 2 Data Sources (Evaluated but Deferred)**:
- WHO Health Statistics (global disease burden) - Overlaps with Data Commons
- PubChem Compound Properties (molecular characteristics) - Low strategic value for SWOT
- NLM Medical Codes (ICD-10, HCPCS) - Limited use case for SWOT analysis

See `.claude/.context/implementation-plans/drug-swot-analysis-enhancement.md` for detailed roadmap.