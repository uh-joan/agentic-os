---
name: get_heart_failure_phase3_trials
description: >
  Retrieves Phase 3 heart failure clinical trials from ClinicalTrials.gov with
  comprehensive endpoint extraction for competitive analysis. Searches using
  multiple heart failure terms (heart failure, HF, cardiac failure, CHF) to
  ensure complete coverage. Extracts primary endpoints and categorizes them
  (mortality, hospitalization, MACE, functional, QoL, composite) for endpoint
  comparison analysis. Includes trial design details, sponsors, and status.

  Trigger keywords: heart failure trials, HF trials, cardiac failure Phase 3,
  heart failure endpoints, HF competitive landscape, cardiovascular trials
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - endpoint_extraction
  - status_aggregation
data_scope:
  total_results: 526
  geographical: Global
  temporal: All time
  phase: Phase 3
created: 2025-11-23
last_updated: 2025-11-23
complexity: medium
execution_time: ~8 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_heart_failure_phase3_trials

## Purpose
Retrieves all Phase 3 heart failure clinical trials with detailed endpoint extraction for competitive analysis. Designed to support strategic assessment of heart failure drug development landscape, endpoint selection strategies, and competitive positioning.

## Usage
This skill is triggered when analyzing:
- Heart failure clinical development landscape
- Phase 3 endpoint strategies in cardiovascular disease
- Competitive intelligence on HF therapeutics
- Endpoint selection for new heart failure trials
- Sponsor activity in advanced-stage HF trials

## Key Features
1. **Comprehensive Search**: Uses multiple HF terminology (heart failure, HF, cardiac failure, CHF)
2. **Endpoint Categorization**: Classifies endpoints into 7 categories:
   - Mortality (death, survival)
   - Hospitalization (admission, readmission)
   - MACE (major adverse cardiovascular events)
   - Exercise/Functional (6MWT, NYHA class)
   - Quality of Life (KCCQ, QoL measures)
   - Composite endpoints
   - Other/Unknown
3. **Full Pagination**: Retrieves all trials using CT.gov's token-based pagination
4. **Rich Metadata**: Extracts NCT ID, title, sponsor, status, enrollment, interventions, study design

## Data Structure
Returns dictionary with:
- `total_count`: Number of Phase 3 HF trials found
- `data`: List of trial dictionaries with extracted fields
- `summary`: Statistics including status distribution, top sponsors, endpoint categories

## Strategic Applications
- **Endpoint Analysis**: Compare endpoint choices across competing programs
- **Competitive Mapping**: Identify active sponsors in Phase 3 HF space
- **Trial Design Insights**: Analyze study design patterns in successful trials
- **Market Timing**: Track recruitment status and completion timelines
- **Partnership Opportunities**: Identify sponsors with multiple programs

## Notes
- Endpoint categorization is keyword-based and may need refinement for novel endpoints
- "Unknown" endpoints suggest manual review may add value
- Composite endpoints dominate (37.6%), reflecting FDA guidance on HF trial design
- Mortality endpoints (27.6%) indicate focus on hard outcomes
