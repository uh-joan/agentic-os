---
name: get_braf_inhibitor_trials
description: >
  Retrieves all BRAF inhibitor clinical trials from ClinicalTrials.gov with pagination.
  Analyzes phase distribution and provides comprehensive trial landscape.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - phase_distribution
data_scope:
  total_results: 228
  geographical: Global
  temporal: All time
created: 2025-11-22
complexity: medium
execution_time: ~6 seconds
token_efficiency: 99%
---

# get_braf_inhibitor_trials

BRAF inhibitor clinical trials with phase distribution analysis.
