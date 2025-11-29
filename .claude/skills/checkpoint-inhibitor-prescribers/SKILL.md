---
name: get_checkpoint_inhibitor_prescribers
description: >
  Identifies top checkpoint inhibitor prescribers from CMS Medicare Part D data.
  Provides institutional analysis, KOL identification, and geographic insights.
category: regulatory
mcp_servers:
  - healthcare_mcp
patterns:
  - json_parsing
  - data_aggregation
  - institutional_analysis
data_scope:
  total_results: 2162
  geographical: United States
  temporal: 2022 Medicare Part D data
created: 2025-11-22
complexity: medium
execution_time: ~15 seconds
---
# get_checkpoint_inhibitor_prescribers


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist Get checkpoint inhibitor prescribers data`
2. `@agent-pharma-search-specialist Show me checkpoint inhibitor prescribers information`
3. `@agent-pharma-search-specialist Find checkpoint inhibitor prescribers details`


Identifies KOLs and major cancer centers for checkpoint inhibitor targeting.

## Key Findings
- 2,162 prescribers, 258,349 claims, $3.45B spend
- Top centers: Houston, NYC, Tampa, Nashville, LA
- Top KOL: Dr. David Waterhouse (Omaha) - 7,851 claims
- Medical Oncology: 85% of prescribers