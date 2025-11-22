---
name: get_diabetes_burden_per_capita
description: >
  Calculates diabetes disease burden per capita by combining WHO prevalence/mortality data
  with Data Commons population statistics. Demonstrates multi-server query pattern.
category: epidemiology
mcp_servers:
  - who_mcp
  - datacommons_mcp
patterns:
  - multi_server_query
  - data_normalization
  - per_capita_calculation
data_scope:
  total_results: 10 countries
  geographical: Global
  temporal: Latest available
created: 2025-11-22
complexity: medium
execution_time: ~8 seconds
token_efficiency: 99%
---

# get_diabetes_burden_per_capita

Diabetes disease burden per capita analysis combining WHO and Data Commons data.
