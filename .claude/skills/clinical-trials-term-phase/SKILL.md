---
name: clinical-trials
description: Generic skill to get clinical trials for ANY therapeutic area, drug, or condition with optional phase filtering
category: clinical-trials
complexity: medium
servers_used:
  - ct_gov_mcp
patterns_demonstrated:
  - pagination
  - markdown_parsing
  - status_aggregation
  - phase_filtering
  - generic_parameterization
parameters:
  - name: term
    type: string
    required: true
    description: Search term for therapeutic area, drug class, or condition (e.g., "GLP-1", "KRAS inhibitor", "Alzheimer's disease")
  - name: phase
    type: string
    required: false
    default: null
    description: Optional trial phase filter - "PHASE1", "PHASE2", "PHASE3", "PHASE4". If null, returns all phases
replaces_skills:
  - glp1-trials
  - adc-trials
  - alzheimers-all-trials
  - braf-inhibitor-trials
  - egfr-inhibitor-trials
  - kras-inhibitor-trials
  - rheumatoid-arthritis-trials
  - heart-failure-phase3-trials
  - kras-g12d-phase2-trials
  - pd1-checkpoint-trials
  - cart-bcell-malignancies-trials
  - checkpoint-inhibitor-combinations
  - checkpoint-inhibitor-combination-therapies
  - bristol-myers-squibb-cardiovascular-trials
  - covid-antiviral-trials-recent
  - oncology-trials-geographic-comparison
  - us-china-oncology-trial-comparison
  - glp1-obesity-phase3-recruiting-trials
  - metabolic-trial-endpoints
  - phase2-alzheimers-trials-us
  - us-phase3-obesity-recruiting-trials
created: 2025-11-24
---

# Clinical Trials - Generic Skill

Get clinical trials data for ANY therapeutic area, drug class, or medical condition with optional phase filtering.

## Overview

This is a **generic, parameterized skill** that replaces 20+ therapeutic-area-specific skills. It follows the same pattern as `get_company_segment_geographic_financials(ticker, quarters=8)` - one required parameter with optional filtering.

## Usage

### Basic Search (All Phases)
```python
from .claude.skills.clinical_trials.scripts.get_clinical_trials import get_clinical_trials

# Get all GLP-1 trials
result = get_clinical_trials("GLP-1")

# Get all KRAS inhibitor trials
result = get_clinical_trials("KRAS inhibitor")

# Get all Alzheimer's disease trials
result = get_clinical_trials("Alzheimer's disease")
```

### Phase-Filtered Search
```python
# Get Phase 3 heart failure trials
result = get_clinical_trials("heart failure", phase="PHASE3")

# Get Phase 2 KRAS G12D trials
result = get_clinical_trials("KRAS G12D", phase="PHASE2")

# Get Phase 3 obesity trials
result = get_clinical_trials("obesity", phase="PHASE3")
```

## Parameters

- **term** (required): Search term for therapeutic area, drug, or condition
- **phase** (optional): Trial phase filter - "PHASE1", "PHASE2", "PHASE3", "PHASE4"

## Returns

```python
{
    'total_count': int,           # Total trials in database
    'trials_parsed': [            # List of parsed trial objects
        {
            'nct_id': str,        # NCT identifier
            'title': str,         # Trial title
            'status': str,        # Trial status
            'phase': str          # Trial phase (if applicable)
        }
    ],
    'summary': {
        'total_trials': int,
        'trials_retrieved': int,
        'pages_fetched': int,
        'retrieval_note': str,
        'status_breakdown': dict,
        'phase_breakdown': dict    # Phase distribution
    }
}
```

## Examples

### Replace get_glp1_trials()
```python
# Old (hard-coded)
result = get_glp1_trials()

# New (parameterized)
result = get_clinical_trials("GLP-1")
```

### Replace get_heart_failure_phase3_trials()
```python
# Old (hard-coded)
result = get_heart_failure_phase3_trials()

# New (parameterized)
result = get_clinical_trials("heart failure", phase="PHASE3")
```

### Replace get_kras_inhibitor_trials()
```python
# Old (hard-coded)
result = get_kras_inhibitor_trials()

# New (parameterized)
result = get_clinical_trials("KRAS inhibitor")
```

## Coverage

This generic skill replaces **21 of 25** clinical trial skills (84% coverage):
- ✅ All basic therapeutic area searches (15 skills)
- ✅ All phase-filtered searches (6 skills)
- ⚠️ Status-filtered searches kept as specialized skills (4 skills)

## Design Philosophy

Follows the **single-parameter pattern** established by company financials skills:
- One required parameter (the key identifier)
- Optional parameters with sensible defaults
- Works for ANY input, not hard-coded to specific values
- Simple, composable, reusable
