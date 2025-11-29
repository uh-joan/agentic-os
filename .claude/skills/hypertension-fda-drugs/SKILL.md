---
name: get_hypertension_fda_drugs
description: >
  Retrieves all FDA-approved drugs for hypertension from FDA database.
  Includes brand names, generic names, and manufacturers with deduplication.
category: drug-discovery
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - deduplication
data_scope:
  total_results: 100
  unique_drugs: 45
  geographical: US
  temporal: All FDA approvals
created: 2025-11-22
complexity: medium
execution_time: ~2 seconds
token_efficiency: 99%
---
# get_hypertension_fda_drugs


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What hypertension drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved hypertension medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for hypertension`


FDA-approved hypertension drugs with manufacturer information.