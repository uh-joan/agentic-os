---
name: get_kras_g12d_phase2_trials
description: >
  Retrieves KRAS G12D inhibitor clinical trials specifically in Phase 2 from ClinicalTrials.gov.
  Searches for G12D-specific mutation programs and returns comprehensive trial details including
  company sponsors, NCT IDs, enrollment timelines, trial status, and initiation dates.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - phase_filtering
data_scope:
  total_results: 15
  phase: Phase 2 only
created: 2025-11-23
complexity: medium
---

# get_kras_g12d_phase2_trials

Retrieves comprehensive data on KRAS G12D inhibitor programs in Phase 2 clinical development.

## Usage

```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/kras-g12d-phase2-trials/scripts/get_kras_g12d_phase2_trials.py
```

## Data Returned

- NCT IDs, company sponsors, trial status, enrollment timelines, start dates
