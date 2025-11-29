---
name: get_orphan_neurological_drugs_approvals
description: >
  Retrieves orphan drugs approved for rare neurological diseases in past 3 years.
  Focuses on ALS, Duchenne, Huntington's, SMA, and other neurological orphan designations.
category: regulatory
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - temporal_filtering
  - category_aggregation
data_scope:
  total_results: 33
  geographical: US
  temporal: Past 3 years
created: 2025-11-22
complexity: medium
execution_time: ~15 seconds
---
# get_orphan_neurological_drugs_approvals


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What orphan neurological drugs approvals drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved orphan neurological drugs approvals medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for orphan neurological drugs approvals`


Retrieves orphan drugs approved for rare neurological diseases.