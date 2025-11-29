---
name: get_alk_rearrangement_trials
description: >
  Retrieves clinical trials for ALK rearrangement positive cancers (primarily
  non-small cell lung cancer). Searches for ALK-positive, ALK fusion, ALK
  rearrangement terminology to capture comprehensive trial landscape. Provides
  status distribution and trial metadata for competitive landscape analysis.

  Trigger keywords: ALK positive, ALK rearrangement, ALK fusion, ALK inhibitor,
  NSCLC ALK, lung cancer ALK
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - markdown_parsing
  - status_aggregation
data_scope:
  total_results: ~150-200
  geographical: Global
  temporal: All time
created: 2025-11-24
last_updated: 2025-11-24
complexity: medium
execution_time: ~3 seconds
token_efficiency: ~98% reduction vs raw data
---
# get_alk_rearrangement_trials


## Sample Queries

Examples of user queries that would trigger reuse of this skill:

1. `@agent-pharma-search-specialist What ALK-positive NSCLC trials are currently recruiting?`
2. `@agent-pharma-search-specialist Show me the ALK rearrangement trial landscape`
3. `@agent-pharma-search-specialist How many ALK inhibitor trials are in development?`
4. `@agent-pharma-search-specialist What's the competitive landscape for ALK fusion positive cancers?`
5. `@agent-pharma-search-specialist Which companies are running ALK-positive lung cancer trials?`


## Purpose
Retrieves all clinical trials for ALK rearrangement positive cancers with status distribution analysis. Designed for competitive landscape assessment in the ALK-positive NSCLC therapeutic space.

## Usage
This skill is triggered when analyzing:
- ALK-positive non-small cell lung cancer trials
- ALK rearrangement therapeutic landscape
- ALK inhibitor competitive intelligence
- Targeted therapy trial activity in ALK+ cancers

## Key Features
1. **Comprehensive Search**: Uses multiple ALK terminology (rearrangement, fusion, positive)
2. **Status Distribution**: Breaks down trials by recruitment/completion status
3. **Basic Search Fields**: NCT ID, Title, Status, Posted Date (phase/sponsor require individual lookups)
4. **Structured Output**: Returns parsed trial data for downstream analysis

## Data Structure
Returns dictionary with:
- `total_count`: Number of ALK rearrangement trials found
- `trials`: List of trial dictionaries with extracted fields
- `status_distribution`: Breakdown by recruitment status

## Strategic Applications
- **Competitive Mapping**: Identify active sponsors in ALK+ space
- **Trial Design Insights**: Analyze trial timing and status patterns
- **Market Timing**: Track recruitment status and completion timelines
- **Partnership Opportunities**: Identify companies with multiple ALK programs

## Notes
- Basic search results only include NCT ID, Title, Status, Posted Date
- For detailed info (phase, sponsor, enrollment), individual CT.gov `get` calls needed
- ALK rearrangements primarily occur in NSCLC but also found in other cancers