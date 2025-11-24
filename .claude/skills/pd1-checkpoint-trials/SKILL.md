---
name: get_pd1_checkpoint_trials
description: >
  Comprehensive analysis of PD-1/PD-L1 checkpoint inhibitor clinical trials across solid tumors.

  Searches ClinicalTrials.gov for major checkpoint inhibitors (pembrolizumab, nivolumab,
  atezolizumab, durvalumab, cemiplimab, avelumab, dostarlimab, retifanlimab, and others)
  across all solid tumor indications.

  Returns detailed breakdown by cancer indication, development phase, company sponsorship,
  and drug-specific trial counts. Includes company × indication matrix showing competitive
  positioning across tumor types.

  Filters out hematologic malignancies to focus on solid tumors only.

  Use cases:
  - Immuno-oncology competitive landscape analysis
  - Checkpoint inhibitor development tracking across indications
  - Company positioning in PD-1/PD-L1 space
  - Indication-specific trial density analysis
  - Drug-specific development patterns

  Trigger keywords: PD-1, PD-L1, checkpoint inhibitor, immuno-oncology, pembrolizumab,
  nivolumab, atezolizumab, solid tumors, cancer immunotherapy
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - indication_categorization
  - company_matrix
  - status_aggregation
data_scope:
  total_results: 5651
  geographical: Global
  temporal: All time
  filters: Solid tumors only (excludes hematologic malignancies)
created: 2025-11-23
last_updated: 2025-11-23
complexity: complex
execution_time: ~15 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_pd1_checkpoint_trials

## Purpose

Retrieve and analyze all PD-1/PD-L1 checkpoint inhibitor clinical trials across solid tumor indications from ClinicalTrials.gov. Provides comprehensive competitive landscape view of the immuno-oncology space.

## Usage

**When to use this skill**:
- Analyzing checkpoint inhibitor competitive landscape across tumor types
- Identifying company positioning in immuno-oncology
- Understanding trial distribution by indication and phase
- Tracking specific checkpoint inhibitor development programs
- Comparing academic vs. industry trial activity
- Identifying underserved solid tumor indications

**Import and use in Python**:
```python
from claude.skills.pd1_checkpoint_trials.scripts.get_pd1_checkpoint_trials import get_pd1_checkpoint_trials

result = get_pd1_checkpoint_trials()
print(f"Total trials: {result['total_count']}")
print(f"Top indication: {result['summary']['top_indications'][0]}")
```

**Execute standalone**:
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/pd1-checkpoint-trials/scripts/get_pd1_checkpoint_trials.py
```

## Data Returned

Returns dictionary with:
- `total_count`: Total solid tumor trials found
- `trials_by_indication`: Trials grouped by cancer type (lung, melanoma, breast, etc.)
- `company_matrix`: Company × indication trial counts (top 15 companies)
- `summary`: Aggregate statistics including:
  - Top 10 indications by trial count
  - Phase distribution (Phase 1, 2, 3, etc.)
  - Status distribution (recruiting, completed, etc.)
  - Top 10 checkpoint inhibitors by mention frequency
  - Top 10 companies by total trial count

## Implementation Details

**Search Strategy**:
- Comprehensive query covering major PD-1/PD-L1 drugs by generic and brand names
- Includes: pembrolizumab, nivolumab, atezolizumab, durvalumab, cemiplimab, avelumab, dostarlimab, retifanlimab, toripalimab, sintilimab, tislelizumab, cosibelimab
- Filters for solid tumors (excludes leukemia, lymphoma, myeloma)

**Pagination**:
- Token-based pagination handling (pageToken parameter)
- Fetches all pages until no nextPageToken returned
- Handles large result sets (5000+ trials)

**Indication Categorization**:
- 16 solid tumor categories based on title/condition keywords
- Major categories: Lung, Melanoma, Breast, GI cancers, GU cancers, Gynecologic, Head & Neck, Sarcoma
- Catch-all "Other Solid Tumors" for rare/mixed indications

**Company Matrix**:
- Tracks top 15 companies by trial count
- Cross-tabulates company × indication for competitive positioning
- Includes academic centers, pharma companies, and biotech

**Data Quality**:
- Verified execution with 5651 solid tumor trials retrieved
- Complete pagination (8 pages fetched)
- Proper filtering of hematologic malignancies
- Schema validation passed

## Example Output

```
Total Trials: 5651
Indications Covered: 16

Top Indications:
  Lung Cancer: 1642 trials
  Other Solid Tumors: 1239 trials
  Melanoma: 634 trials
  Gastric Cancer: 399 trials
  Breast Cancer: 351 trials

Phase Distribution:
  Phase 2: 2317 trials
  Phase 1: 1146 trials
  Phase 3: 891 trials

Top Checkpoint Inhibitors:
  Pembrolizumab: 2187 mentions
  Nivolumab: 1764 mentions
  Atezolizumab: 903 mentions
  Durvalumab: 749 mentions

Top Companies:
  M.D. Anderson Cancer Center: 271 trials
  National Cancer Institute: 176 trials
  Merck Sharp & Dohme: 168 trials
```

## Related Skills

- `get_kras_inhibitor_trials` - Targeted therapy trials
- `get_cart_cell_therapy_trials` - CAR-T therapy trials
- `get_adc_approved_drugs` - FDA-approved antibody-drug conjugates
- `get_company_segment_geographic_financials` - Company financial analysis

## Notes

- Execution time: ~15 seconds for full dataset
- Returns 5600+ trials across 16 solid tumor categories
- Excludes hematologic malignancies (leukemia, lymphoma, myeloma)
- Company matrix limited to top 15 companies for readability
- Drug tracking covers major approved and investigational checkpoint inhibitors
