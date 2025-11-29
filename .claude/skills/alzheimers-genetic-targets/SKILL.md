---
name: get_alzheimers_genetic_targets
description: >
  Retrieves genetic targets and drug associations for Alzheimer's disease from Open Targets Platform.
  Queries for disease entity, associated genetic targets with evidence scores, and known drugs.
  Returns top 10 targets ranked by association score with evidence breakdown by data type.
  Use when analyzing Alzheimer's therapeutic targets, drug discovery opportunities, or genetic validation.
  Keywords: Alzheimer's, neurodegeneration, genetic targets, target validation, drug discovery, APOE, APP, PSEN1.
category: target-validation
mcp_servers:
  - opentargets_mcp
patterns:
  - disease_search
  - target_association
  - evidence_aggregation
  - json_parsing
data_scope:
  total_results: 20 targets analyzed
  geographical: Global
  temporal: Current Open Targets data
created: 2025-11-22
last_updated: 2025-11-22
complexity: medium
execution_time: ~4 seconds
token_efficiency: ~99% reduction vs raw data
---
# get_alzheimers_genetic_targets


## Sample Queries

Examples of user queries that would trigger reuse of this skill:

1. `@agent-pharma-search-specialist What are the top genetically validated targets for Alzheimer's disease?`
2. `@agent-pharma-search-specialist Show me Alzheimer's targets with strong genetic evidence and existing drugs`
3. `@agent-pharma-search-specialist Which Alzheimer's targets have the highest association scores in Open Targets?`
4. `@agent-pharma-search-specialist Find novel drug discovery opportunities for Alzheimer's beyond APOE and APP`
5. `@agent-pharma-search-specialist What genetic evidence supports emerging Alzheimer's therapeutic targets?`


Queries Open Targets Platform to retrieve genetic targets associated with Alzheimer's disease.