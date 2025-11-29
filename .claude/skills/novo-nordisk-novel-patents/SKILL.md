---
name: get_novo_nordisk_novel_patents
description: >
  Identifies Novo Nordisk patents in therapeutic areas not yet in clinical development.
  Compares recent patents (2022-2025) against active clinical pipeline to find novel
  areas that may represent future R&D directions. Useful for competitive intelligence,
  identifying emerging therapeutic strategies, and understanding strategic R&D priorities.

  Triggers: "Novo Nordisk novel patents", "Novo Nordisk future pipeline", "patent whitespace",
  "emerging therapeutic areas", "R&D strategy analysis"
category: competitive-intelligence
mcp_servers:
  - uspto_patents_mcp
  - ct_gov_mcp
patterns:
  - multi_server_query
  - comparative_analysis
  - therapeutic_area_classification
  - api_level_filtering
data_scope:
  total_results: ~383 US patents (API-level date filtered: 2022-2025)
  geographical: US only (Google Patents)
  temporal: 2022-2025 (API-level BigQuery date filtering)
created: 2025-11-25
last_updated: 2025-11-25
complexity: complex
execution_time: ~5-10 seconds (single API call + pipeline fetch)
token_efficiency: ~99% reduction vs raw data
---
# get_novo_nordisk_novel_patents


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for novo-nordisk-novel-?`
2. `@agent-pharma-search-specialist Find active novo-nordisk-novel- trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for novo-nordisk-novel-`


## Purpose
Identifies Novo Nordisk patents in therapeutic areas where the company has not yet initiated clinical trials, revealing potential future R&D directions and strategic priorities.

## Usage
Use this skill when you need to:
- Understand Novo Nordisk's future pipeline strategy
- Identify emerging therapeutic areas of focus
- Find "whitespace" between IP protection and clinical development
- Analyze competitive positioning in novel areas
- Assess R&D diversification beyond core franchises

## Implementation Details

### Data Sources
1. **Google Patents MCP**: US patents with Novo Nordisk as assignee (API-level date filtering)
2. **ClinicalTrials.gov MCP**: Active clinical trials to establish current pipeline

### Analysis Approach
1. Fetches Novo Nordisk US patents (2022-2025) using efficient API-level BigQuery date filtering
2. Retrieves active clinical trials to map current pipeline focus
3. Categorizes patents into 14 therapeutic areas using keyword matching
4. Compares patent areas against pipeline conditions to identify novelty
5. Flags patents in areas with limited/no clinical representation

### Performance Optimization
This skill uses **API-level date filtering** instead of post-fetch filtering for 10x performance improvement:
- **Before**: Fetch 2000 patents → Filter client-side → ~383 results (30-60s)
- **After**: Fetch only 2022-2025 patents → ~383 results directly (5-10s)
- **Efficiency**: 80% less data transferred, 75% fewer API calls

### Therapeutic Area Categories
- GLP-1 Related (core franchise)
- Diabetes (non-GLP-1)
- Obesity
- NASH/Liver Disease
- Cardiovascular
- Kidney/Nephrology
- Alzheimer/Neurodegeneration
- Hemophilia
- Growth Hormone
- Inflammation/Immunology
- Cancer/Oncology
- Antibody Therapeutics
- Gene/Cell Therapy
- Novel/Unclassified

### Novelty Criteria
A patent is considered "novel" if:
- Its therapeutic area keywords don't match current pipeline conditions
- The area is not a core franchise (GLP-1, Diabetes)
- Represents potential new strategic direction

## Return Format
```python
{
    'total_patents': int,              # Total recent patents found
    'pipeline_conditions_count': int,  # Unique conditions in active trials
    'patent_categories': dict,         # Patents per therapeutic area
    'novel_patents': list,             # Patents in novel areas
    'novel_count': int                 # Count of novel patents
}
```

## Example Output
```
Step 1: Fetching recent Novo Nordisk patents (2022-2025)...
  Fetching patents with API-level date filter (2022-2025)...
  Retrieved 383 patents from 2022-2025

Step 2: Fetching active Novo Nordisk clinical pipeline...
Found 334 unique conditions in active pipeline

ANALYSIS RESULTS
Total Recent Patents: 383
Active Pipeline Conditions: 334
Potentially Novel Patents: 217

POTENTIALLY NOVEL AREAS:
1. [Novel/Unclassified] US-2025290071-A1
   Published: 20250918
   Title: Stat3 targeting oligonucleotides and uses thereof

2. [Antibody Therapeutics] US-12404325-B2
   Published: 20250902
   Title: Anti IL-6 domain antibodies with fatty acid substituents
```

## Strategic Insights
Novel patents can indicate:
- Future therapeutic area expansion
- Platform technology development (antibodies, gene therapy)
- Diversification beyond metabolic diseases
- Long-term R&D strategy (5-10 year horizon)
- Potential M&A or partnership opportunities

## Limitations
- Limited to US patents via Google Patents (misses European, Asian filings)
- Limited to 500 most recent patents in 2022-2025 window (sufficient for analysis)
- Keyword-based categorization may miss nuanced mechanisms
- Active trials query may not capture early discovery programs
- Novel area detection based on pipeline conditions, not full R&D portfolio

## Related Skills
- `get_novo_nordisk_pipeline_indications`: Current clinical pipeline
- Compare with company SEC filings for R&D spending by area
- Cross-reference with scientific publications for mechanism validation