---
name: get_kras_inhibitor_trials
description: >
  Get KRAS inhibitor clinical trials from ClinicalTrials.gov. Basic implementation without pagination (may miss trials if >1000 results). Use when analyzing KRAS inhibitor pipeline, competitive landscape. Consider upgrading to pagination pattern for complete data. Keywords: KRAS, KRAS G12C, oncology, cancer, targeted therapy, clinical trials.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - basic_ct_gov_search
  - markdown_parsing
data_scope:
  total_results: 363
  geographical: Global
  temporal: All time
created: 2025-11-19
last_updated: 2025-11-19
complexity: simple
execution_time: ~2 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_kras_inhibitor_trials

## Purpose
Get KRAS inhibitor clinical trials across all phases and statuses.

## Returns
- `dict`: Dictionary containing:
  - `total_count` (int): Total number of KRAS inhibitor trials found
  - `trials_summary` (str): Markdown-formatted summary with trial details

## Usage
```python
from .claude.skills.kras_inhibitor_trials.scripts.get_kras_inhibitor_trials import get_kras_inhibitor_trials

results = get_kras_inhibitor_trials()
print(f"Total trials: {results['total_count']}")
print(results['trials_summary'])
```

## MCP Tools Used
- `mcp__ct-gov-mcp__ct_gov_studies` (search method)

## Query Parameters
- **term**: "KRAS inhibitor"
- **pageSize**: 100 (returns first 100 of total results)

## Response Format
ClinicalTrials.gov returns markdown string containing:
- Search parameters used
- Total count of matching studies
- List of trials with:
  - NCT ID
  - Title
  - Status (Recruiting, Completed, Terminated, etc.)
  - Posted date
  - Link to full study details

## Example Output
```python
{
    'total_count': 363,
    'trials_summary': '# Clinical Trials Search Results\n\n**Results:** 100 of 363 studies found...'
}
```

## Notes
- Searches across all phases (Phase 1, 2, 3, 4)
- Searches across all statuses (recruiting, completed, terminated, etc.)
- Returns first 100 detailed results but reports total count
- For more specific filtering, modify search parameters (phase, status, location)

## Related Skills
- `get_kras_g12c_trials` - Filter for KRAS G12C-specific trials
- `get_recruiting_kras_trials` - Filter for actively recruiting trials only
