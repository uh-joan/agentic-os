---
name: get_cart_manufacturing_patents
description: >
  Searches USPTO patents for CAR-T manufacturing innovations including bioreactors,
  automation, scale-up, and cost reduction technologies.
category: intellectual-property
mcp_servers:
  - uspto_patents_mcp
patterns:
  - json_parsing
  - technology_analysis
  - assignee_aggregation
data_scope:
  total_results: 100
  geographical: United States
  temporal: All USPTO data
created: 2025-11-22
complexity: medium
execution_time: ~4 seconds
---
# get_cart_manufacturing_patents


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What patents exist for CAR-T cell therapy?`
2. `@agent-pharma-search-specialist Show me the IP landscape for CAR-T cell therapy`
3. `@agent-pharma-search-specialist Find CAR-T cell therapy patents`


Identifies CAR-T manufacturing IP landscape for technology licensing and COGS optimization.

## Key Applications
- Technology licensing opportunities
- Manufacturing innovation tracking
- Cost reduction strategies
- Competitive intelligence