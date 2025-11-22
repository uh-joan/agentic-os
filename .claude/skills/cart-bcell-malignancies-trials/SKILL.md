---
name: get_cart_bcell_malignancies_trials
description: >
  Retrieves all recruiting CAR-T cell therapy clinical trials for B-cell malignancies
  from ClinicalTrials.gov. Captures trials targeting CD19, CD22, BCMA, and other B-cell
  antigens. Includes combination therapies and novel CAR-T constructs.

  Use cases: Technology platform assessment, partnership opportunity identification,
  competitive landscape analysis for CAR-T developers, clinical development planning.

  Trigger keywords: CAR-T, CAR T-cell, chimeric antigen receptor, B-cell malignancy,
  B-cell lymphoma, multiple myeloma, CD19, CD22, BCMA, recruiting trials.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - status_filtering
  - target_identification
data_scope:
  geographical: Global
  temporal: Active recruiting trials
  disease_focus: B-cell malignancies
  technology: CAR-T cell therapy
created: 2025-11-21
last_updated: 2025-11-21
complexity: medium
execution_time: ~5 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_cart_bcell_malignancies_trials

## Purpose

Retrieves comprehensive data on recruiting CAR-T cell therapy trials for B-cell malignancies from ClinicalTrials.gov. This skill focuses on active recruitment opportunities across all phases of clinical development.

## Key Features

- **Target Identification**: Parses trial data to identify specific CAR-T targets (CD19, CD22, BCMA, etc.)
- **Combination Therapy Detection**: Identifies trials combining CAR-T with other agents
- **Pagination Handling**: Ensures complete dataset retrieval across all result pages
- **Status Filtering**: Focuses exclusively on "Recruiting" trials for current opportunities

## Use Cases

1. **Technology Platform Assessment**: Evaluate CAR-T construct designs and targets
2. **Partnership Opportunities**: Identify trials suitable for collaboration
3. **Competitive Landscape**: Map competitive positioning in CAR-T space
4. **Clinical Development Planning**: Understand trial design trends and endpoints

## Data Collected

- Trial identifiers (NCT ID)
- Phase of development
- Target antigens (CD19, CD22, BCMA, etc.)
- Combination therapies
- Geographic locations
- Patient populations
- Primary endpoints
- Sponsor information

## Implementation Details

Uses ClinicalTrials.gov search with intervention and condition filters:
- Intervention: "CAR-T cell therapy" OR "chimeric antigen receptor"
- Condition: "B-cell malignancy" OR related terms
- Status: Recruiting only
- Pagination: Token-based to capture all results
