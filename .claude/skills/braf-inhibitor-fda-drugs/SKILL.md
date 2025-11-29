---
name: get_braf_inhibitor_fda_drugs
description: Infrastructure validation test skill
category: testing
mcp_servers:
  - ct_gov_mcp
patterns:
  - json_parsing
data_scope:
  total_results: 10
created: 2025-11-22
complexity: simple
execution_time: ~2s
---
# get_braf_inhibitor_fda_drugs


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What BRAF inhibitor drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved BRAF inhibitor medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for BRAF inhibitor`


Infrastructure test skill for comprehensive MCP server validation.