---
name: get_obesity_drugs_early_development
description: >
  Identifies FDA-approved obesity drugs with active early-stage (Phase 1 or Phase 2)
  development programs. Multi-server query correlating FDA approvals with ongoing
  ClinicalTrials.gov studies. Returns drugs with BOTH regulatory approval AND
  continued R&D investment. Useful for competitive intelligence, lifecycle management
  analysis, and identifying drugs with expansion potential beyond initial indication.

  Trigger keywords: obesity drugs development, early stage trials approved drugs,
  lifecycle management obesity, post-approval development programs, obesity pipeline
category: competitive-intelligence
mcp_servers:
  - fda_mcp
  - ct_gov_mcp
patterns:
  - multi_server_query
  - json_parsing
  - markdown_parsing
  - cross_reference
data_scope:
  total_results: 6 FDA approved obesity drugs, all 6 with active early development (502 total trials)
  geographical: Global (FDA + global trials)
  temporal: All approved drugs + current active trials
created: 2025-11-25
last_updated: 2025-11-25
complexity: complex
execution_time: ~45 seconds
token_efficiency: ~99% reduction vs raw data
---
# get_obesity_drugs_early_development


## Sample Queries

Examples of user queries that would invoke the pharma-search-specialist to create or use this skill:

1. `@agent-pharma-search-specialist What obesity drugs are FDA approved?`
2. `@agent-pharma-search-specialist Show me all approved obesity medications`
3. `@agent-pharma-search-specialist Get the list of FDA-approved drugs for obesity`


## Purpose

Identifies FDA-approved obesity drugs that have active early-stage (Phase 1 or Phase 2) clinical development programs. This multi-server analysis reveals which approved drugs continue to have R&D investment, indicating:

- **Lifecycle Management**: Companies investing in line extensions
- **New Indications**: Exploring uses beyond obesity
- **Formulation Improvements**: Next-generation versions
- **Combination Therapies**: Testing with other agents
- **Competitive Activity**: Where innovation continues post-approval

## Usage

**When to use this skill:**
- Competitive intelligence on obesity market
- Lifecycle management strategy assessment
- Identifying drugs with expansion potential
- Portfolio analysis of approved products
- Market evolution forecasting

**Example queries:**
- "Which obesity drugs have ongoing early development?"
- "Show me approved obesity drugs with active R&D"
- "What's the lifecycle management strategy for obesity drugs?"

## Multi-Server Strategy

This skill demonstrates the **cross-reference pattern**:

1. **FDA Query**: Get all approved obesity drugs
   - Server: `fda_mcp`
   - Format: JSON
   - Data: Brand names, generic names, approval dates

2. **For Each Drug → CT.gov Query**: Find Phase 1/2 trials
   - Server: `ct_gov_mcp`
   - Format: Markdown
   - Query: `"{drug_name}" AND (AREA[Phase] PHASE1 OR AREA[Phase] PHASE2)`

3. **Correlation**: Match approved drugs to active trials
   - Filter: Only drugs with >0 early-stage trials
   - Aggregate: Count by phase, include trial examples

## Implementation Details

**FDA Parsing:**
- Extracts brand and generic names from `openfda` structure
- Identifies approval dates from submissions data
- Handles missing data gracefully with `.get()` methods

**CT.gov Parsing:**
- Regex-based markdown parsing (CT.gov returns markdown, not JSON)
- Pattern: `r'###\s+\d+\.\s+NCT\d{8}'` to split trials
- Extracts phase, status, title from each trial block
- Counts Phase 1 vs Phase 2 separately

**Cross-Reference Logic:**
- Queries CT.gov once per approved drug (~83 queries)
- Parses markdown responses to count trials
- Only includes drugs with >0 early-stage trials
- Returns top 5 trial examples per drug

**Return Format:**
```python
{
    'drugs_with_development': [
        {
            'drug_name': 'WEGOVY',
            'brand_name': 'WEGOVY',
            'generic_name': 'semaglutide',
            'approval_date': '2021-06-04',
            'total_early_trials': 17,
            'phase1_trials': 13,
            'phase2_trials': 4,
            'trials': [...]  # First 5 trials
        },
        ...
    ],
    'total_approved': 83,
    'total_with_early_trials': 8,
    'summary': '...'  # Formatted text summary
}
```

## Key Insights

From latest execution (2025-11-25):
- **6 FDA-approved obesity drugs** identified using known drug names (FDA best practice)
- **All 6 drugs** have active Phase 1/2 development (100% pipeline activity)
- **502 total early-stage trials** across all obesity drugs
- **semaglutide** leads with 218 trials (112 Phase 1, 106 Phase 2) - GLP-1 class expansion
- **liraglutide** has 140 trials (72 Phase 1, 68 Phase 2) - robust lifecycle management
- **tirzepatide** has 83 trials (31 Phase 1, 52 Phase 2) - newer GIP/GLP-1 dual agonist
- Even older drugs (orlistat, phentermine) continue development (20-28 trials each)
- Balanced Phase 1/2 distribution indicates both mechanism studies and efficacy exploration

## Patterns Demonstrated

1. **Multi-Server Orchestration**: Sequential queries across FDA + CT.gov
2. **Format Handling**: JSON (FDA) + Markdown (CT.gov) in one skill
3. **Cross-Reference**: Correlating data from different sources
4. **Deduplication**: Using drug names as keys to match records
5. **Graceful Degradation**: Handles missing data without failing

## Performance

- **Execution Time**: ~45 seconds (83 FDA drugs × ~0.5s per CT.gov query)
- **Token Efficiency**: ~99% reduction (processes 83 drugs + trials in-memory)
- **Data Volume**: 83 FDA records + hundreds of trial records → summary only

## Dependencies

```python
import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import search_drugs
from mcp.servers.ct_gov_mcp import search
import re
```

## Example Output

```
============================================================
FDA-APPROVED OBESITY DRUGS WITH EARLY-STAGE DEVELOPMENT
============================================================

Total FDA-approved obesity drugs: 83
Drugs with Phase 1/2 trials: 8

Drugs with Active Early Development Programs:
------------------------------------------------------------

WEGOVY
  Brand: WEGOVY
  Generic: semaglutide
  Approval Date: 2021-06-04
  Early-Stage Trials: 17 (Phase 1: 13, Phase 2: 4)

  Example Trials:
    • NCT06649799: Effect of Semaglutide on Cardiac Structure and Function...
      Phase: PHASE1, Status: RECRUITING
    • NCT05052177: Semaglutide Effects on Heart Disease and Stroke...
      Phase: PHASE2, Status: RECRUITING
...
```

## Future Enhancements

- Add Phase 3 trials for comprehensive pipeline view
- Include sponsor information for competitive analysis
- Track trial start dates to measure development velocity
- Add geographic breakdown of trial locations
- Include combination therapy identification