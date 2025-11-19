---
name: get_us_phase3_obesity_recruiting_trials
description: >
  Get Phase 3 obesity trials recruiting in the United States from ClinicalTrials.gov. Combines multiple filters (phase, status, location) for precise pipeline analysis. Use when analyzing late-stage obesity drug development or US recruitment opportunities. Keywords: obesity, Phase 3, recruiting, United States, weight loss, clinical trials.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - ct_gov_multi_filter
  - phase_status_location_filtering
data_scope:
  total_results: varies
  geographical: US
  temporal: Current
created: 2025-11-19
last_updated: 2025-11-19
complexity: simple
execution_time: ~2 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_us_phase3_obesity_recruiting_trials

## Purpose
Get count of Phase 3 obesity clinical trials that are actively recruiting in the United States.

## Parameters
None

## Returns
- `int`: Number of Phase 3 obesity trials actively recruiting in the US

## Usage
```python
from .claude.skills.us_phase3_obesity_recruiting_trials.scripts.get_us_phase3_obesity_recruiting_trials import get_us_phase3_obesity_recruiting_trials
count = get_us_phase3_obesity_recruiting_trials()
print(f"Found {count} trials")
```

## Example Output
```
36
```

## MCP Tools Used
- ct_gov_studies (via ct-gov-mcp client)

## Query Parameters
- Condition: obesity
- Phase: PHASE3
- Status: recruiting
- Location: United States
