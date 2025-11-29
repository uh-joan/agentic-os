---
name: get_orphan_neurological_drugs
description: >
  Retrieves FDA orphan drug approvals for rare neurological diseases from the past 3 years.
  Queries FDA database for drugs treating SMA, Duchenne, ALS, Huntington's, multiple sclerosis,
  epilepsy, ataxia, myasthenia gravis, and other neurodegenerative diseases.
category: regulatory
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - date_filtering
  - deduplication
  - multi_query_aggregation
data_scope:
  total_results: 27
  geographical: United States
  temporal: Past 3 years (rolling window)
created: 2025-11-22
complexity: medium
execution_time: ~8 seconds
---
# get_orphan_neurological_drugs


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What orphan neurological drugs drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved orphan neurological drugs medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for orphan neurological drugs`


Retrieves FDA orphan drug approvals for rare neurological diseases over the past 3 years.

## Key Findings

- 27 total orphan drug approvals (past 3 years)
- 2024: 12 approvals (most active year)
- 2023: 9 approvals
- 2022: 6 approvals
- Top manufacturers: Sanofi-Aventis, Biogen, PTC Therapeutics
- Most common routes: Intravenous, Oral