---
name: get_checkpoint_inhibitor_combination_therapies
description: >
  Analyzes combination therapy patterns in checkpoint inhibitor clinical trials.
  Searches ClinicalTrials.gov for checkpoint inhibitor trials and extracts combination
  patterns including most common partner drugs, checkpoint inhibitor usage frequency,
  and phase distribution.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - pattern_analysis
  - text_extraction
data_scope:
  total_results: 3681
  combination_trials: 2803
  geographical: Global
  temporal: All time
created: 2025-11-22
complexity: complex
execution_time: ~15 seconds
---

# get_checkpoint_inhibitor_combination_therapies

Analyzes combination therapy patterns in checkpoint inhibitor trials.

## Key Findings

- 3,681 total checkpoint inhibitor trials
- 2,803 combination trials (76.1% of all trials)
- Top checkpoint inhibitors: Pembrolizumab, Nivolumab, Atezolizumab
- Most common partners: Chemotherapy, Carboplatin, Pemetrexed
- Phase distribution analyzed across all combinations
