---
name: get_phase2_alzheimers_trials_us
description: >
  Get Phase 2 Alzheimer's disease trials in the United States from ClinicalTrials.gov. Filters by phase and geography for targeted pipeline analysis. Use when analyzing mid-stage Alzheimer's development pipeline or US-specific trial activity. Keywords: Alzheimer's, Phase 2, United States, neurology, dementia, clinical trials.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - ct_gov_phase_filtering
  - geographic_filtering
data_scope:
  total_results: varies
  geographical: US
  temporal: All time
created: 2025-11-19
last_updated: 2025-11-19
complexity: simple
execution_time: ~2 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_phase2_alzheimers_trials_us

## Purpose
Find Phase 2 clinical trials for Alzheimer's disease that are actively recruiting in the United States.

## Usage
```python
from .claude.skills.phase2_alzheimers_trials_us.scripts.get_phase2_alzheimers_trials_us import get_phase2_alzheimers_trials_us

results = get_phase2_alzheimers_trials_us()
print(f"Found {results['total_trials']} trials")
```

## Returns
Dictionary with:
- `total_trials`: Number of trials found
- `unique_sponsors`: Number of unique sponsors
- `total_enrollment`: Total planned enrollment
- `trials`: List of trial dictionaries (nct_id, title, sponsor, enrollment, etc.)
- `sponsor_list`: Sorted list of unique sponsors

## MCP Server
- **Server**: ct_gov_mcp
- **Tool**: ct_gov_studies
- **Parameters**: query="Alzheimer's disease", phase="PHASE2", status="RECRUITING", location="United States"

## Example Output
```
Total Trials Found: 75
Unique Sponsors: 67
Total Planned Enrollment: 16,772 participants
```

## Created
2025-11-18
