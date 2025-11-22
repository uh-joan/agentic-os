---
name: get_ra_targets_and_trials
description: >
  Combines Open Targets genetic data with ClinicalTrials.gov trial data for rheumatoid arthritis.
  Gets top 10 genetic targets based on association score, matches with recruiting trials.
category: target-validation
mcp_servers:
  - opentargets_mcp
  - ct_gov_mcp
patterns:
  - multi_server_query
  - disease_search
  - target_association
  - pagination
  - markdown_parsing
  - data_integration
data_scope:
  total_results: 339 (10 targets + 329 trials)
  geographical: Global
  temporal: Current (recruiting trials)
created: 2025-11-22
complexity: complex
execution_time: ~15 seconds
token_efficiency: 99%
---

# get_ra_targets_and_trials

Rheumatoid arthritis genetic targets with active clinical trial matching.
