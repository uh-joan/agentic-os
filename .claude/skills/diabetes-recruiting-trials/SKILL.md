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

Recruiting diabetes trials with type categorization and phase distribution.
