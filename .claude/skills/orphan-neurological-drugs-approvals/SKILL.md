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

Retrieves orphan drugs approved for rare neurological diseases.
