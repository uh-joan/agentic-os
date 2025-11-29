---
name: get_trials_by_phase_and_design
description: >
  Find clinical trials filtered by phase AND study design characteristics.
  Essential for regulatory experts assessing impact of new design requirements.
  Enables filtering by phase combined with allocation type, intervention model,
  masking level, and primary purpose to identify trials matching specific
  methodological criteria.

  Trigger keywords: regulatory impact, design requirements, study design,
  randomized trials, blinding requirements, allocation method, intervention model
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - multi_parameter_filtering
  - design_aggregation
data_scope:
  total_results: varies by filters
  geographical: Global
  temporal: All time
created: 2025-11-28
last_updated: 2025-11-28
complexity: medium
execution_time: ~3-5 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_trials_by_phase_and_design

## Purpose

Find clinical trials filtered by both phase AND study design characteristics. This skill is essential for regulatory experts assessing the impact of new design requirements on existing trial portfolios.

## Key Features

- **Multi-parameter filtering**: Combine phase with design characteristics
- **Design breakdown**: Aggregates trials by allocation, intervention model, masking, and purpose
- **Regulatory focus**: Identify trials affected by new methodological requirements
- **Complete pagination**: Retrieves all matching trials

## Usage

### Basic Phase + Design Filter
```python
from .claude.skills.trials_by_phase_and_design.scripts.get_trials_by_phase_and_design import get_trials_by_phase_and_design

# Find Phase 3 diabetes trials using randomized parallel design
result = get_trials_by_phase_and_design(
    therapeutic_area="diabetes",
    phase="PHASE3",
    allocation="randomized",
    intervention_model="parallel"
)
```

### Regulatory Impact Assessment
```python
# Find cardiovascular trials WITHOUT double-blind masking
# (to assess impact of new blinding requirements)
result = get_trials_by_phase_and_design(
    therapeutic_area="cardiovascular",
    phase="PHASE3",
    masking="none"
)
```

### Early Development Design Analysis
```python
# Find Phase 2 oncology trials using single-arm design
# (common in early oncology development)
result = get_trials_by_phase_and_design(
    therapeutic_area="oncology",
    phase="PHASE2",
    intervention_model="single"
)
```

## Parameters

### Required
- **therapeutic_area** (str): Disease/condition (e.g., "diabetes", "oncology", "cardiovascular")
- **phase** (str): Trial phase (e.g., "PHASE1", "PHASE2", "PHASE3", "PHASE4")

### Optional Design Filters
- **allocation** (str): Allocation type (e.g., "randomized", "nonrandomized", "na")
- **intervention_model** (str): Study design (e.g., "parallel", "crossover", "factorial", "sequential", "single")
- **masking** (str): Blinding level (e.g., "none", "single", "double", "triple", "quadruple")
- **primary_purpose** (str): Study purpose (e.g., "treatment", "prevention", "diagnostic", "supportive")

## Return Structure

```python
{
    'total_count': int,
    'trials_summary': str,  # Markdown summary with breakdowns
    'design_breakdown': {
        'allocation': {'randomized': X, 'nonrandomized': Y, ...},
        'intervention_model': {'parallel': X, 'crossover': Y, ...},
        'masking': {'none': X, 'single': Y, 'double': Z, ...},
        'primary_purpose': {'treatment': X, 'prevention': Y, ...}
    },
    'matching_trials': [
        {
            'nct_id': str,
            'title': str,
            'phase': str,
            'status': str,
            'allocation': str,
            'intervention_model': str,
            'masking': str,
            'primary_purpose': str
        }
    ]
}
```

## Implementation Details

### CT.gov API Mapping
- Uses `condition` parameter for therapeutic area
- Uses `phase` parameter directly
- Maps `intervention_model` to CT.gov's `assignment` parameter
- Supports `allocation`, `masking`, and `purpose` filters

### Pagination Handling
- Retrieves all results using `pageSize=1000` and `pageToken` iteration
- Ensures complete dataset for accurate design breakdowns

### Markdown Parsing
- Extracts design characteristics from each trial block
- Handles optional fields gracefully (defaults to "Not Specified")
- Aggregates by design category for regulatory impact analysis

## Use Cases

1. **Regulatory Impact Assessment**: Identify trials affected by new design requirements
2. **Methodological Analysis**: Compare design approaches across therapeutic areas
3. **Portfolio Planning**: Understand design landscape before initiating trials
4. **Compliance Review**: Find trials needing design modifications for new regulations
5. **Competitive Intelligence**: Analyze competitors' design strategies by phase

## Example Output

```
## Trials by Phase and Design: Diabetes

**Filters Applied**: Phase: PHASE3, Condition: diabetes, Allocation: randomized, Intervention Model: parallel

**Total Trials Found**: 289

### Design Breakdown

**Allocation:**
  - Randomized: 289 (100.0%)

**Intervention Model:**
  - Parallel Assignment: 265 (91.7%)
  - Crossover Assignment: 18 (6.2%)
  - Factorial Assignment: 6 (2.1%)

**Masking:**
  - Quadruple: 156 (54.0%)
  - Double: 78 (27.0%)
  - Triple: 32 (11.1%)
  - None (Open Label): 23 (7.9%)

### Status Distribution
  - Completed: 142 (49.1%)
  - Active, not recruiting: 58 (20.1%)
  - Recruiting: 45 (15.6%)
  - Not yet recruiting: 28 (9.7%)
  - Terminated: 16 (5.5%)
```

## Notes

- All design parameters are optional - can filter by phase alone if needed
- Design breakdown shows actual distribution, not just filtered subset
- Useful for understanding design trends and regulatory compliance gaps
- Results include all trials matching specified filters (no sampling)
