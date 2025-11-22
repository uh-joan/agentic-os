---
name: get_glp1_obesity_phase3_recruiting_trials
description: >
  Retrieves all Phase 3 obesity trials using GLP-1 agonists that are currently recruiting in the United States.
  Includes pagination to capture complete dataset. Useful for competitive intelligence, portfolio prioritization,
  and market landscape analysis. Trigger keywords: GLP-1, obesity, Phase 3, recruiting, US trials, glucagon-like peptide.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - status_filtering
  - geographic_filtering
data_scope:
  total_results: 118
  geographical: United States
  temporal: Currently recruiting
  phase: Phase 3
  therapeutic_area: Obesity + GLP-1 agonists
created: 2025-01-21
last_updated: 2025-01-21
complexity: medium
execution_time: ~3 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_glp1_obesity_phase3_recruiting_trials

## Purpose
Retrieves comprehensive data on Phase 3 obesity trials using GLP-1 agonists currently recruiting in the United States. This skill provides critical competitive intelligence for pharmaceutical companies and investors tracking the GLP-1 market.

## Usage
Use this skill when you need to:
- Assess competitive landscape in GLP-1 obesity space
- Identify recruiting trials for partnership opportunities
- Analyze trial design and endpoints across competitors
- Track market entry timing based on trial progress
- Evaluate geographic distribution of US trial sites

## Implementation Details
- **Data Source**: ClinicalTrials.gov via ct_gov_mcp server
- **Query Strategy**: Multi-filter approach (obesity + GLP-1 + Phase 3 + recruiting + US geography)
- **Pagination**: Token-based pagination captures all 118 trials
- **Response Format**: Markdown parsed via regex patterns
- **Geographic Scope**: 2000-mile radius from US center point (39.8°N, 98.6°W)

## Data Structure
Returns dictionary with:
- `total_count`: Number of trials found
- `data`: List of trial objects with NCT ID, title, phase, status, locations
- `summary`: Query parameters and metadata

## Business Value
Enables strategic decisions around:
- Portfolio prioritization (identify white space opportunities)
- Competitive positioning (understand trial landscape)
- Partnership evaluation (find complementary programs)
- Market timing (assess pipeline maturity)
