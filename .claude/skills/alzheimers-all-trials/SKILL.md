---
name: get_alzheimers_all_trials
description: Get all Alzheimer's disease clinical trials across all phases and mechanisms
category: clinical-trials
servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - multi_phase_collection
complexity: medium
created: 2025-11-23
---

# Alzheimer's Disease Clinical Trials Collection

Comprehensive collection of all Alzheimer's disease clinical trials from ClinicalTrials.gov,
including all phases (Early Phase 1, Phase 1, Phase 2, Phase 3, Phase 4) and all mechanisms
of action beyond anti-amyloid antibodies.

## Function Signature

```python
get_alzheimers_all_trials() -> dict
```

## Returns

Dictionary containing:
- `total_count`: Total number of trials found
- `trials_by_phase`: Breakdown by clinical phase
- `trials_by_status`: Breakdown by recruitment status
- `mechanism_categories`: Trials categorized by mechanism of action
- `summary`: Formatted summary string

## Mechanisms Tracked

- Anti-amyloid antibodies
- Tau aggregation inhibitors
- BACE inhibitors
- Gamma-secretase modulators
- Neuroinflammation modulators (TREM2, complement)
- Synaptic plasticity enhancers
- Metabolic interventions (APOE4, lipid metabolism)
- Neuroprotective agents
- Other novel mechanisms

## Usage

```python
from claude.skills.alzheimers_all_trials.scripts.get_alzheimers_all_trials import get_alzheimers_all_trials

result = get_alzheimers_all_trials()
print(result['summary'])
print(f"Total trials: {result['total_count']}")
print(f"Trials by phase: {result['trials_by_phase']}")
```
