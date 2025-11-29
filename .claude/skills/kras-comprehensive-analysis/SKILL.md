---
name: get_kras_comprehensive_analysis
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
# get_kras_comprehensive_analysis


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for KRAS inhibitor?`
2. `@agent-pharma-search-specialist Find active KRAS inhibitor trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for KRAS inhibitor`


Infrastructure test skill for comprehensive MCP server validation.