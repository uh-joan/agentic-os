---
name: get_glp1_obesity_patents
description: >
  Search USPTO patent database for GLP-1 receptor agonist patents related to obesity treatment.
  Retrieves patent titles, abstracts, filing dates, and identifies key assignees/companies.
  Analyzes patent trends by year and provides top patent holders analysis.
category: regulatory
mcp_servers:
  - uspto_patents_mcp
patterns:
  - json_parsing
  - data_aggregation
  - trend_analysis
data_scope:
  total_results: 45
  geographical: US
  temporal: All time
created: 2025-11-22
complexity: medium
execution_time: ~2 seconds
---
# get_glp1_obesity_patents


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What patents exist for GLP-1 receptor agonist?`
2. `@agent-pharma-search-specialist Show me the IP landscape for GLP-1 receptor agonist`
3. `@agent-pharma-search-specialist Find GLP-1 receptor agonist patents`


Searches USPTO patent database for GLP-1 receptor agonist patents in obesity treatment.