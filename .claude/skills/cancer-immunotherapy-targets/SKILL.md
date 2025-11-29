---
name: get_cancer_immunotherapy_targets
description: >
  Identifies validated targets for cancer immunotherapy beyond PD-1/PD-L1 checkpoint inhibitors.
  Searches Open Targets for immune checkpoint, T-cell activation, and immune modulation targets
  with cancer associations. Filters out PD-1/PD-L1 to focus on next-generation opportunities.
  Returns targets prioritized by clinical precedence, antibody tractability, and cancer indications.

  Use this skill when exploring:
  - Next-generation checkpoint inhibitors
  - Novel immunotherapy targets
  - Cancer immunology drug targets
  - Therapeutic antibody opportunities
  - Immune modulation mechanisms

  Keywords: immunotherapy, checkpoint inhibitor, T-cell, immune checkpoint, tumor immunology,
  cancer immunotherapy, therapeutic target, antibody tractable, clinical precedence
category: target-validation
mcp_servers:
  - opentargets_mcp
patterns:
  - multi_term_search
  - json_parsing
  - deduplication
  - prioritization
data_scope:
  total_results: 58
  geographical: Global
  temporal: Current validated targets
created: 2025-11-22
last_updated: 2025-11-22
complexity: medium
execution_time: ~15 seconds
token_efficiency: ~99% reduction vs raw data
---
# get_cancer_immunotherapy_targets


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What are the genetic targets for PD-1 checkpoint inhibitor?`
2. `@agent-pharma-search-specialist Show me therapeutic targets for PD-1 checkpoint inhibitor`
3. `@agent-pharma-search-specialist Find validated targets in PD-1 checkpoint inhibitor`


## Purpose
Discovers and prioritizes validated targets for cancer immunotherapy beyond the well-established PD-1/PD-L1 checkpoint inhibitors, enabling next-generation therapeutic development.

## Usage
Execute this skill when you need to:
- Identify novel immunotherapy targets for cancer
- Explore alternatives to PD-1/PD-L1 inhibitors
- Assess antibody tractability for immune targets
- Find targets with clinical precedence in oncology
- Discover emerging checkpoint inhibitor opportunities

## Business Value
- **Pipeline Innovation**: Identify next-generation checkpoint inhibitors
- **Competitive Differentiation**: Move beyond crowded PD-1/PD-L1 space
- **Target Validation**: Leverage genetic evidence and clinical precedence
- **Strategic Planning**: Assess antibody vs small molecule opportunities
- **Risk Mitigation**: Focus on clinically validated mechanisms

## Implementation Details

### Search Strategy
Queries Open Targets using multiple immunotherapy-related terms:
- Immune checkpoint mechanisms
- T-cell activation pathways
- Tumor immunology targets
- Cytotoxic T lymphocyte markers
- Natural killer cell receptors

### Filtering Logic
- **Excludes**: PD-1 (PDCD1/ENSG00000188389) and PD-L1 (CD274/ENSG00000120217)
- **Deduplicates**: Removes targets found via multiple search terms
- **Focuses**: Cancer-associated indications only

### Prioritization Criteria
Targets sorted by:
1. Clinical precedence (adverse effects data = clinical experience)
2. Antibody tractability (Clinical Precedence tier)
3. Number of cancer indications

### Data Extracted
For each target:
- Gene symbol and Ensembl ID
- Full target name
- Antibody tractability assessment
- Small molecule tractability assessment
- Top 3 cancer indications
- Clinical precedence indicator
- Discovery search term

## Output Format

### Summary Statistics
- Total validated targets found
- Antibody tractable targets (Clinical Precedence)
- Small molecule tractable targets
- Targets with clinical precedence

### Top 15 Priority Targets
Detailed information for highest-priority targets including:
- Target identification (symbol, ID, name)
- Tractability assessments
- Cancer indication associations
- Clinical precedence status

### Complete Dataset
Full list of all discovered targets for detailed analysis

## Example Output
```
================================================================================
CANCER IMMUNOTHERAPY TARGETS (Beyond PD-1/PD-L1)
================================================================================

Total validated targets found: 58
Antibody tractable (Clinical Precedence): 32
Small molecule tractable (Clinical Precedence): 18
Targets with clinical precedence: 45

================================================================================
TOP 15 PRIORITY TARGETS:
================================================================================

1. CTLA4 (ENSG00000163599)
   Name: cytotoxic T-lymphocyte associated protein 4
   Antibody Tractability: Clinical Precedence
   Clinical Precedence: Yes
   Cancer Indications: melanoma, lung cancer, bladder cancer

2. LAG3 (ENSG00000089692)
   Name: lymphocyte activating 3
   Antibody Tractability: Clinical Precedence
   Clinical Precedence: Yes
   Cancer Indications: melanoma, non-small cell lung cancer

[... additional targets ...]
```

## Related Skills
- `get_target_disease_associations` - Deep dive into specific target-disease links
- `get_target_safety_profile` - Assess adverse effects and clinical safety
- `get_clinical_trials_by_target` - Find trials testing specific targets

## Notes
- Excludes PD-1/PD-L1 to focus on next-generation opportunities
- Prioritizes targets with both genetic evidence and clinical precedence
- Antibody tractability particularly relevant for checkpoint inhibitors
- Cancer indications extracted from Open Targets disease associations