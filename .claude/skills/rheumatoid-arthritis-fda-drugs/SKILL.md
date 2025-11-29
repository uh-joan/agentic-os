---
name: get_rheumatoid_arthritis_fda_drugs
description: >
  Retrieves all FDA-approved drugs for rheumatoid arthritis from FDA drug labels database.
  Includes biologics and small molecules with approval dates and manufacturers.
category: drug-discovery
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - deduplication
data_scope:
  total_results: 45
  geographical: US
  temporal: All FDA approvals
created: 2025-11-22
complexity: medium
execution_time: ~2 seconds
token_efficiency: 99%
---
# get_rheumatoid_arthritis_fda_drugs


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What rheumatoid arthritis drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved rheumatoid arthritis medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for rheumatoid arthritis`


FDA-approved rheumatoid arthritis drugs with biologics/small molecule categorization.