---
name: get_cvd_burden_per_capita
description: >
  Calculate cardiovascular disease burden per capita by combining WHO mortality data
  with Data Commons population statistics. Analyzes 15 countries, deaths per 100k.
category: epidemiology
mcp_servers:
  - who_mcp
  - datacommons_mcp
patterns:
  - multi_server_query
  - data_normalization
  - error_handling
data_scope:
  total_countries: 15
  geographical: Global
  temporal: Most recent
created: 2025-11-22
complexity: medium
execution_time: ~5 seconds
token_efficiency: 99%
---

# get_cvd_burden_per_capita

CVD mortality burden per capita analysis combining WHO and Data Commons data.
