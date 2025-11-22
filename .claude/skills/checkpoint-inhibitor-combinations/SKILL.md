---
name: get_checkpoint_inhibitor_combinations
description: >
  Analyzes combination therapy patterns in checkpoint inhibitor clinical trials.
  Searches ClinicalTrials.gov for major checkpoint inhibitors and categorizes
  their combination partners by drug class. Provides frequency analysis of most
  common combinations and identifies emerging trends.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - combination_analysis
  - drug_categorization
data_scope:
  total_results: 1729
  geographical: Global
  temporal: All time
  checkpoint_inhibitors: 7
created: 2025-11-22
last_updated: 2025-11-22
complexity: high
execution_time: ~15 seconds
token_efficiency: ~99% reduction
---

# get_checkpoint_inhibitor_combinations

Analyzes combination therapy patterns in checkpoint inhibitor clinical trials.
