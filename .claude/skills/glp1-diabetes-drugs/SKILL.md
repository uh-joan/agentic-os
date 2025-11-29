---
name: get_glp1_diabetes_drugs
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
# get_glp1_diabetes_drugs


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for GLP-1 receptor agonist?`
2. `@agent-pharma-search-specialist Find active GLP-1 receptor agonist trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for GLP-1 receptor agonist`


Infrastructure test skill for comprehensive MCP server validation.