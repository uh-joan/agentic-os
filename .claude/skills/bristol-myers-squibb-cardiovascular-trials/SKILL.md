---
name: get_bristol_myers_squibb_cardiovascular_trials
description: >
  Retrieves comprehensive dataset of Bristol Myers Squibb cardiovascular clinical trials
  from ClinicalTrials.gov across all phases and statuses. Uses intelligent pagination
  to ensure complete data retrieval (275 trials across 3 pages). Provides distribution
  analysis by trial status and phase. Ideal for competitive intelligence, pipeline analysis,
  cardiovascular R&D strategy, and Bristol Myers Squibb cardiovascular portfolio assessment.
  Trigger keywords: "Bristol Myers Squibb cardiovascular", "BMS heart", "BMS cardiology trials",
  "Bristol cardiovascular pipeline".
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - status_aggregation
  - phase_aggregation
data_scope:
  total_results: 275
  geographical: Global
  temporal: All time
  company: Bristol Myers Squibb
  therapeutic_area: Cardiovascular
created: 2025-11-23
last_updated: 2025-11-23
complexity: medium
execution_time: ~8 seconds
token_efficiency: ~99% reduction vs raw data
---
# get_bristol_myers_squibb_cardiovascular_trials


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for cardiovascular disease?`
2. `@agent-pharma-search-specialist Find active cardiovascular disease trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for cardiovascular disease`


## Purpose
Retrieves and analyzes Bristol Myers Squibb's complete cardiovascular clinical trials portfolio from ClinicalTrials.gov. Provides comprehensive view of BMS cardiovascular R&D activities across all trial phases and statuses.

## Usage
Use this skill when you need:
- Bristol Myers Squibb cardiovascular pipeline analysis
- BMS cardiology trial portfolio assessment
- Competitive intelligence on BMS heart disease programs
- Historical view of BMS cardiovascular R&D
- Status distribution of BMS cardiovascular trials
- Phase progression analysis of BMS cardiology studies

## Data Retrieved
- **Total trials**: 275 cardiovascular trials
- **Status breakdown**: Completed (197), Terminated (41), Active not recruiting (17), Recruiting (9), Withdrawn (6), Unknown (5)
- **Phase breakdown**: Phase 3 (160), Phase 2 (59), Phase 4 (25), Phase 1 (10), and others
- **Coverage**: All historical and current BMS cardiovascular trials
- **Pagination**: 3 pages fetched for complete dataset

## Implementation Details

### Query Strategy
- **Primary query**: "Bristol Myers Squibb cardiovascular"
- **Pagination**: Token-based with 1000 results per page
- **Response format**: CT.gov markdown (requires regex parsing)

### Proven Patterns Applied
Adapted from `get_glp1_trials` reference skill:
1. **Pagination logic**: Token-based loop until no more pages
2. **Markdown parsing**: Regex-based trial block extraction
3. **Status aggregation**: Dictionary counting with frequency sorting
4. **Phase aggregation**: Additional distribution analysis
5. **Return format**: Consistent structure with summary statistics

### Technical Approach
- Regex pattern `###\s+\d+\.\s+NCT\d{8}` to split trial blocks
- Field extraction via `\*\*Field:\*\*\s*(.+?)(?:\n|$)` pattern
- Graceful handling of optional fields (not all trials have all metadata)
- Page token detection: `` `pageToken:\s*"([^"]+)"` ``

## Return Format
```python
{
    'total_count': 275,
    'trials': [...],  # Raw trial data
    'summary': {
        'total_count': 275,
        'status_distribution': {...},
        'phase_distribution': {...},
        'pages_fetched': 3
    }
}
```

## Example Output
```
Bristol Myers Squibb Cardiovascular Trials Summary
============================================================
Total trials found: 275
Pages fetched: 3

Status Distribution:
  Completed: 197
  Terminated: 41
  Active, not recruiting: 17
  Recruiting: 9
  ...

Phase Distribution:
  Phase 3: 160
  Phase 2: 59
  Phase 4: 25
  ...
```

## Key Insights from Data
- **Mature portfolio**: 197 completed trials (72% completion rate)
- **Phase 3 focus**: 160 trials in Phase 3 (58% of portfolio)
- **Active pipeline**: 9 recruiting trials currently
- **Historical scope**: Comprehensive view across all BMS cardiovascular history

## Related Skills
- `get_bristol_myers_squibb_oncology_trials` - BMS oncology portfolio
- `get_cardiovascular_trials` - All cardiovascular trials (multi-sponsor)
- `get_company_segment_geographic_financials` - BMS financial performance

## Verification Status
✅ All checks passed:
- Execution: Success
- Data retrieval: 275 trials
- Pagination: Complete (3 pages, no truncation)
- Executable: Standalone capable
- Schema: Valid trial summary format