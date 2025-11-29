---
name: get_diabetes_recruiting_trials
description: >
  Retrieves all currently recruiting diabetes clinical trials from ClinicalTrials.gov.
  Includes phase distribution and diabetes type categorization (Type 1, Type 2, Gestational).
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - categorization
  - status_filtering
data_scope:
  total_results: 9090
  geographical: Global
  temporal: Currently recruiting
created: 2025-11-22
complexity: medium
execution_time: ~12 seconds
token_efficiency: 99%
---
# get_diabetes_recruiting_trials


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What clinical trials are running for diabetes?`
2. `@agent-pharma-search-specialist Find active diabetes trials`
3. `@agent-pharma-search-specialist Show me the clinical development landscape for diabetes`


Recruiting diabetes trials with type categorization and phase distribution.