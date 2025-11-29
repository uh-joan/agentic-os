---
name: get_2024_breakthrough_therapy_drugs
description: >
  Retrieves FDA-approved drugs from 2024 with analysis of potential breakthrough therapy
  designations. Provides comprehensive analysis of approval timelines, therapeutic areas,
  manufacturers, and pharmacological classes.
category: regulatory
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - timeline_analysis
  - therapeutic_area_aggregation
data_scope:
  total_results: 33
  geographical: US (FDA)
  temporal: 2024 (January-December)
created: 2025-11-22
complexity: medium
execution_time: ~3 seconds
---
# get_2024_breakthrough_therapy_drugs


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What 2024 breakthrough therapy drugs drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved 2024 breakthrough therapy drugs medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for 2024 breakthrough therapy drugs`


Analyzes FDA drug approvals from 2024 to identify potential breakthrough therapy designations.

## Key Insights

- 33 total FDA approvals in 2024
- Average review timeline: 356 days (range: 119-1,005 days)
- Product mix: 76% NDA, 24% BLA
- Top manufacturer: Takeda (3 approvals)
- Dominant route: ORAL (64%)
- Context: Watershed year for cell & gene therapy (13 CGT approvals)