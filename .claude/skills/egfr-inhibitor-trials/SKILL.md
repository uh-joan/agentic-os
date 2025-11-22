---
name: get_egfr_inhibitor_trials
description: >
  Retrieves comprehensive clinical trials data for EGFR inhibitors from ClinicalTrials.gov
  across all phases. Complete enumeration with pagination, phase distribution, status breakdown.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - phase_distribution
  - status_aggregation
data_scope:
  total_results: 1179
  geographical: Global
  temporal: All time
created: 2025-11-22
complexity: medium
execution_time: ~4 seconds
token_efficiency: 99%
---

# get_egfr_inhibitor_trials

Comprehensive EGFR inhibitor clinical trials data with phase and status analysis.
