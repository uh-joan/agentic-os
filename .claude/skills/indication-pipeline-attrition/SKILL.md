---
name: get_indication_pipeline_attrition
description: >
  Track terminated and withdrawn clinical trials for any therapeutic area to identify
  failure patterns and competitive intelligence. Analyzes attrition by phase, sponsor,
  and intervention type. Useful for understanding clinical development risks, competitive
  failures, and de-risking investment decisions. Trigger keywords: "attrition", "terminated",
  "withdrawn", "failed trials", "pipeline failures", "development risks".
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - status_filtering
  - sponsor_aggregation
  - phase_breakdown
data_scope:
  total_results: Full analysis (all terminated/withdrawn trials)
  geographical: Global
  temporal: All time
created: 2025-11-25
last_updated: 2025-11-25
complexity: medium
execution_time: ~10-30 seconds (depends on trial count)
token_efficiency: ~99% reduction vs raw data
---
# get_indication_pipeline_attrition


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for indication pipeline attrition?`
2. `@agent-pharma-search-specialist Find active indication pipeline attrition trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for indication pipeline attrition`


## Purpose
Track terminated and withdrawn clinical trials for any therapeutic area to identify failure patterns, competitive intelligence, and development risks.

## Usage
Use this skill when you need to:
- Assess clinical development risks for a therapeutic area
- Identify which companies have had trial failures
- Understand common failure points (Phase 1, 2, 3)
- De-risk investment decisions based on attrition patterns
- Competitive intelligence on failed programs

## Parameters
- `indication` (str): Therapeutic area, drug class, or mechanism
  - Examples: "KRAS inhibitor", "obesity", "GLP-1", "Alzheimer's"
- `sample_size` (int, optional): Number of trials to analyze in detail (default: None = full analysis)

## Returns
Dictionary containing:
- `indication`: The therapeutic area analyzed
- `total_terminated`: Count of terminated trials
- `total_withdrawn`: Count of withdrawn trials
- `total_attrition`: Total failed trials found by CT.gov query
- `sample_size`: Number of trials actually analyzed in detail
- `analyzed_trials`: Trials with complete phase/sponsor data
- `phase_breakdown`: Attrition by development phase
- `top_sponsors`: Top 10 sponsors with most failures
- `interventions`: Sample list of failed interventions
- `summary`: Human-readable analysis

## Implementation Details

### Query Strategy
1. Searches CT.gov for trials matching indication
2. Filters for status: TERMINATED or WITHDRAWN
3. Uses pagination to capture all results (pageSize=1000)
4. Parses markdown to extract trial metadata

### Analysis Dimensions
- **Phase Distribution**: Counts failures by Phase 1, 2, 3, 4
- **Sponsor Patterns**: Identifies top sponsors with most failures
- **Status Breakdown**: Separates terminated vs withdrawn
- **Intervention Extraction**: Lists failed drug candidates

### Data Quality
- Complete pagination ensures all attrition captured
- Markdown parsing handles CT.gov response format
- Robust field extraction with regex patterns
- Handles missing/optional fields gracefully

## Example Output
```
Pipeline Attrition Analysis for KRAS inhibitor
============================================================

Total Attrition: 78 trials
  - Terminated: 65
  - Withdrawn: 13

Phase Breakdown:
  - Phase 1: 28
  - Phase 2: 35
  - Phase 3: 12
  - Phase 4: 1
  - Other/Not Applicable: 2

Top 5 Sponsors with Failed Trials:
  1. Amgen: 8 trials
  2. Mirati Therapeutics Inc.: 6 trials
  3. Boehringer Ingelheim: 5 trials
  4. Revolution Medicines, Inc.: 4 trials
  5. Memorial Sloan Kettering Cancer Center: 3 trials
```

## Use Cases
1. **Investment Due Diligence**: Assess clinical risk before investing
2. **Competitive Analysis**: Identify which competitors have failed programs
3. **Development Strategy**: Understand common failure points to avoid
4. **Market Timing**: Gauge field maturity based on attrition rates
5. **Partnership Evaluation**: Vet potential partners' track record

## Related Skills
- `get_indication_drug_pipeline_breakdown`: Active pipeline analysis
- `get_{therapeutic_area}_trials`: All trials for comparison
- `get_company_segment_geographic_financials`: Financial impact of failures